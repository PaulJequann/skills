# Navigation

Navigation is the part a screenshot cannot show, and users feel it within ten
seconds. Every transition answers three questions: how did the user get here,
must they be able to come back, and what does back (the chevron, the iOS edge
swipe, Android back) do afterwards. The API names are Expo Router's; the
meaning carries to any navigator.

1. **Push goes deeper, replace moves on.** `router.push` when the user will
   want to return. `router.replace` or `<Redirect>` when returning would land
   in a state the world has moved past. `router.dismissTo(href)` to finish a
   flow and land on a known screen. Back undoes navigation, never an event.
2. **Presentation is meaning.** A self-contained task with steps is
   `presentation: 'modal'` with its own stack, its own header, and its own
   Cancel and Done. A short interruption such as a picker, filters, or item
   options is a `formSheet` with detents and drag-to-dismiss. Immersive
   content is a `fullScreenModal` with an explicit close. Something floating
   over a still-visible screen, such as a confirm card, a lightbox, or a coach
   mark, is a `transparentModal`. Destructive
   confirmation is an action sheet. Item actions are a native context menu.
   Sharing, browsing, and photo picking use the system controller, never a
   rebuilt route. A sheet that grows a second step was a modal all along. If a
   link could reach it, it is a route, not a `useState` sheet.
3. **One-way doors leave the stack.** Sign-in on an app that requires it,
   completed onboarding including the skip path, a purchase, and a finished
   session. Guard them with `Stack.Protected` and land with `replace`, so
   back cannot re-enter the old state. Android back
   from home exits the app rather than showing the login screen, and a paid
   paywall never reopens. Keep the user's place at the same time. Sign-in
   demanded by one action is a modal over the screen that action was taken on,
   and a paywall opened from a feature dismisses back onto that feature,
   unlocked, rather than replacing to the tabs root.
4. **Block back in exactly two cases.** An irreversible request in flight, for
   seconds, with visible progress, and unsaved work in a modal, after asking. Both use
   `usePreventRemove` on the modal's root screen.
   Transient in-screen state such as selection mode or an expanded search
   consumes the first back, and the second back leaves. Anything else that
   traps back, such as a funnel or a rating prompt, is a defect. The edge swipe
   and the iOS interactive pop work everywhere else.
5. **Tabs are peers.** No slide between tabs, each tab keeps its own stack, and
   re-tapping the active tab pops that tab to its root. Full-attention screens
   such as a composer, a player, or a checkout live above the tabs in the root
   stack. A tab bar has three to five items, labels always on,
   and the filled symbol for the active tab. Every screen is reachable by
   URL, and a deep link lands with a real stack underneath, through
   `initialRouteName` or `withAnchor`. A cold start holds the splash until
   session state resolves, then lands by state, so no login flashes before
   home.
6. **Study the grammar, not just the pixels.** While studying a winning flow,
   note what each step is, whether a push, a modal, or a sheet, and match that
   consistency.
