#!/usr/bin/env node

// Turns a review agent's raw event stream into one validated review package.
//
// Everything except DECODERS is agent-agnostic: the review grammar, extraction,
// normalization, and validation are the shared contract that makes a review from
// one agent interchangeable with a review from another.

import fs from "node:fs";
import { pathToFileURL } from "node:url";

const BEGIN_MARKER = "BEGIN_REVIEW";
const END_MARKER = "END_REVIEW";
const FINDING_HEADER_PATTERN =
  /^\d+\. (LOW|MEDIUM|HIGH|CRITICAL) \| [^|]+ \| .+$/;

function parseEvents(eventStream) {
  const messages = [];

  for (const [index, rawLine] of eventStream.split(/\r?\n/).entries()) {
    if (!rawLine.trim()) continue;

    try {
      messages.push(JSON.parse(rawLine));
    } catch {
      throw new Error(
        `transport event stream contains invalid JSON at line ${index + 1}`,
      );
    }
  }

  return messages;
}

// ---------------------------------------------------------------------------
// Decoders — the only transport-specific surface.
//
// Each maps a raw event stream to { text, usage }. Add a decoder only when a
// transport's wire format genuinely differs; agents sharing a transport share a
// decoder.
// ---------------------------------------------------------------------------

const DECODERS = {
  // acpx --format json --json-strict → raw ACP JSON-RPC NDJSON.
  acp(eventStream) {
    const chunks = [];
    let usage = null;

    for (const message of parseEvents(eventStream)) {
      const update = message?.params?.update;

      if (
        message?.method === "session/update" &&
        update?.sessionUpdate === "agent_message_chunk" &&
        update?.content?.type === "text"
      ) {
        chunks.push(update.content.text);
      }

      // Usage placement is not uniform across ACP agents: grok-build reports it
      // on a turn_completed update, copilot only on the terminal prompt result.
      const raw =
        (update?.sessionUpdate === "turn_completed" ? update.usage : null) ??
        message?.result?.usage;

      if (raw) {
        usage = {
          input_tokens: raw.inputTokens,
          output_tokens: raw.outputTokens,
          total_tokens: raw.totalTokens,
          cached_read_tokens: raw.cachedReadTokens,
          reasoning_tokens: raw.reasoningTokens ?? raw.thoughtTokens,
          model_calls: raw.modelCalls,
          turns: raw.numTurns,
        };
      }
    }

    return { text: chunks.join(""), usage };
  },

  // copilot --output-format json → Copilot-native JSONL envelopes.
  "copilot-jsonl"(eventStream) {
    const chunks = [];
    let usage = null;

    for (const message of parseEvents(eventStream)) {
      if (message?.type === "assistant.message") {
        const content = message?.data?.content;
        // Tool-call turns emit an assistant.message with empty content.
        if (typeof content === "string" && content) chunks.push(content);
      }

      if (message?.type === "result") {
        const raw = message.usage ?? {};
        usage = {
          ...(usage ?? {}),
          premium_requests: raw.premiumRequests,
          api_duration_ms: raw.totalApiDurationMs,
          session_duration_ms: raw.sessionDurationMs,
        };
      }

      if (message?.type === "session.usage_checkpoint") {
        usage = { ...(usage ?? {}), nano_aiu: message?.data?.totalNanoAiu };
      }
    }

    return { text: chunks.join(""), usage };
  },
};

export function decode(decoderId, eventStream) {
  const decoder = DECODERS[decoderId];
  if (!decoder) {
    throw new Error(
      `unknown decoder "${decoderId}"; known: ${Object.keys(DECODERS).join(", ")}`,
    );
  }
  return decoder(eventStream);
}

// A transport that fails before the agent speaks reports why in the event
// stream rather than on stderr. Surfacing it turns "produced no assistant text"
// into an actionable diagnosis (bad auth, missing model, startup timeout).
export function extractTransportError(eventStream) {
  let message = null;

  for (const event of parseEvents(eventStream)) {
    // JSON-RPC (ACP) errors, and Copilot's error-shaped envelopes.
    const candidate =
      event?.error?.message ??
      (event?.type === "error" ? event?.data?.message : null) ??
      (event?.type === "session.error" ? event?.data?.message : null);

    if (typeof candidate === "string" && candidate.trim()) {
      message = candidate.trim().replace(/\s+/g, " ");
    }
  }

  return message;
}

export function formatUsageMetadata(usage) {
  if (!usage) return null;

  const values = Object.entries(usage)
    .filter(([, value]) => Number.isFinite(value))
    .map(([key, value]) => `${key}=${value}`);

  return values.length > 0 ? `usage=${values.join(" ")}` : null;
}

// ---------------------------------------------------------------------------
// Shared review contract
// ---------------------------------------------------------------------------

export function extractLastCompleteReview(assistantText) {
  let endSearchFrom = 0;
  let lastCompleteReview = null;

  while (true) {
    const end = assistantText.indexOf(END_MARKER, endSearchFrom);
    if (end === -1) break;

    const begin = assistantText.lastIndexOf(BEGIN_MARKER, end);
    if (begin !== -1) {
      lastCompleteReview = assistantText.slice(begin, end + END_MARKER.length);
    }
    endSearchFrom = end + END_MARKER.length;
  }

  return lastCompleteReview;
}

// Agents reliably produce the right information in the wrong shape. Fold the
// known-equivalent layout back into the canonical one rather than failing a
// review that is otherwise complete.
function normalizeFindingHeaders(lines) {
  const normalized = [...lines];

  for (let index = 0; index < normalized.length; index += 1) {
    const severity = normalized[index].match(
      /^(\d+)\.\s+severity:\s*(low|medium|high|critical)\s*$/i,
    );
    if (!severity) continue;

    const category = normalized[index + 1]?.match(/^category:\s*(.+)$/i);
    const path = normalized[index + 2]?.match(/^path:\s*(.+)$/i);
    if (!category || !path) continue;

    normalized.splice(
      index,
      3,
      `${severity[1]}. ${severity[2].toUpperCase()} | ${category[1].trim()} | ${path[1].trim()}`,
    );
  }

  return normalized;
}

export function normalizeReview(review) {
  const lineNormalized = review.replace(/\r\n?/g, "\n").trimEnd();
  let lines = lineNormalized.split("\n");

  if (lines[0] !== BEGIN_MARKER || lines.at(-1) !== END_MARKER) {
    throw new Error("review package markers are malformed");
  }

  lines = normalizeFindingHeaders(lines);
  const body = lines.slice(1, -1);
  const firstContent = body.find((line) => line.trim() !== "");

  if (!/^status: (clean|findings)$/.test(firstContent ?? "")) {
    throw new Error(
      "review package must begin with status: clean or status: findings",
    );
  }

  const statusLines = body.filter((line) =>
    /^status: (clean|findings)$/.test(line),
  );
  if (statusLines.length !== 1) {
    throw new Error(
      "review package must contain exactly one status: clean or status: findings line",
    );
  }

  if (firstContent === "status: clean") {
    const content = body.filter((line) => line.trim() !== "");
    const allowed = new Set([
      "status: clean",
      "summary: No actionable findings.",
    ]);
    if (
      content.some((line) => !allowed.has(line)) ||
      content.filter((line) => line === "summary: No actionable findings.")
        .length > 1
    ) {
      throw new Error("clean review package contains unexpected content");
    }

    return [
      BEGIN_MARKER,
      "status: clean",
      "summary: No actionable findings.",
      END_MARKER,
    ].join("\n");
  }

  return lines.join("\n");
}

export function validateReview(review, maxOutputBytes) {
  const lineNormalized = review.replace(/\r\n?/g, "\n").trimEnd();
  const size = Buffer.byteLength(`${lineNormalized}\n`);
  if (size > maxOutputBytes) {
    throw new Error(
      `review package is ${size} bytes; limit is ${maxOutputBytes}`,
    );
  }

  const normalized = normalizeReview(lineNormalized);
  const lines = normalized.split("\n");
  const status = lines.find((line) => /^status: (clean|findings)$/.test(line));
  const findingIndexes = lines.flatMap((line, index) =>
    FINDING_HEADER_PATTERN.test(line) ? [index] : [],
  );

  if (status === "status: clean") {
    if (findingIndexes.length !== 0) {
      throw new Error("clean review package must not contain findings");
    }
    return `${normalized}\n`;
  }

  if (findingIndexes.length === 0) {
    throw new Error(
      "findings review package does not contain a formatted finding",
    );
  }
  if (lines.includes("summary: No actionable findings.")) {
    throw new Error("findings review package must not contain the clean summary");
  }

  const requiredFields = [
    ["Failure", /^Failure: .+$/],
    ["Evidence", /^Evidence: .+$/],
    ["Fix", /^Fix: .+$/],
    ["Test or Validation", /^(Test|Validation): .+$/],
  ];

  for (const [findingOffset, findingIndex] of findingIndexes.entries()) {
    const nextFindingIndex =
      findingIndexes[findingOffset + 1] ?? lines.length - 1;
    const finding = lines.slice(findingIndex + 1, nextFindingIndex);

    for (const [field, pattern] of requiredFields) {
      if (finding.filter((line) => pattern.test(line)).length !== 1) {
        throw new Error(`each finding must contain exactly one ${field} field`);
      }
    }
  }

  return `${normalized}\n`;
}

function parsePositiveInteger(value, name) {
  if (!/^[1-9]\d*$/.test(value)) {
    throw new Error(`${name} must be a positive integer`);
  }
  return Number(value);
}

function main() {
  const [
    decoderId,
    eventsPath,
    assistantPath,
    reviewPath,
    maxOutputBytesValue,
    metadataPath,
  ] = process.argv.slice(2);

  if (
    !decoderId ||
    !eventsPath ||
    !assistantPath ||
    !reviewPath ||
    !maxOutputBytesValue ||
    !metadataPath
  ) {
    throw new Error(
      "usage: parse-review.mjs <decoder> <events> <assistant> <review> <max-bytes> <metadata>",
    );
  }

  const maxOutputBytes = parsePositiveInteger(
    maxOutputBytesValue,
    "max output bytes",
  );
  const eventStream = fs.readFileSync(eventsPath, "utf8");
  const { text, usage } = decode(decoderId, eventStream);

  const usageMetadata = formatUsageMetadata(usage);
  if (usageMetadata) fs.appendFileSync(metadataPath, `${usageMetadata}\n`);

  fs.writeFileSync(assistantPath, text);
  if (!text) {
    const transportError = extractTransportError(eventStream);
    throw new Error(
      transportError
        ? `transport produced no assistant text events: ${transportError}`
        : "transport produced no assistant text events",
    );
  }

  const review = extractLastCompleteReview(text);
  if (!review) {
    throw new Error("output contains no complete review package");
  }

  fs.writeFileSync(reviewPath, review);
  fs.writeFileSync(reviewPath, validateReview(review, maxOutputBytes));
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  try {
    main();
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`review parser: ${message}\n`);
    process.exitCode = 1;
  }
}
