# Archived Frontend Surfaces

These files were removed from the active app surface because their matching backend stacks are archived or no longer canonical.

Archived here:
- legacy v4 production shell and styles
- standalone campaign page
- standalone branding page

Active production UI now uses:
- `pages/ProductLaunchPage.jsx` for campaigns, branding, and publishing
- `pages/CommandCenterPage.jsx` for agent and autonomous operations
- `pages/ProjectsPage.jsx` is routed again because the live backend `/api/projects/*` surface still exists