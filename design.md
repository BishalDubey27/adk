# Tech Sarathi — UI/UX Design Specification
> Input file for Snitch.ai | AI-Powered Project Management System
> **Team:** Tech Sarathi | **Hackathon:** NIRMAN — Amity University Mumbai

---

## Table of Contents
1. [Product Summary](#1-product-summary)
2. [Design Principles](#2-design-principles)
3. [Design Tokens](#3-design-tokens)
4. [Layout & Navigation](#4-layout--navigation)
5. [Pages & Screens](#5-pages--screens)
6. [Shared Components](#6-shared-components)
7. [Forms](#7-forms)
8. [States & Feedback](#8-states--feedback)
9. [Responsive Behaviour](#9-responsive-behaviour)
10. [Iconography](#10-iconography)
11. [Animations & Transitions](#11-animations--transitions)
12. [Accessibility](#12-accessibility)

---

## 1. Product Summary

**Tech Sarathi** is an AI-powered project management dashboard. A multi-agent backend automatically assigns tasks, monitors risk, and escalates low-confidence decisions to a human PM. The UI must surface confidence scores, live project health, and a human review queue in a clean, professional interface.

**Primary User:** Project Manager (PM)
**Secondary User:** Team Member (read-only task view)
**Platform:** Web (desktop-first, responsive down to tablet)
**Frontend Stack:** React 18 + Vite + Tailwind CSS

---

## 2. Design Principles

- **Clarity over density** — the PM needs to scan many projects at once; avoid information overload.
- **Confidence-first** — every card, task, and decision must visually communicate its AI confidence score.
- **Action-oriented** — escalations and risk flags must be impossible to miss; primary CTAs are always visible.
- **Audit transparency** — every automated decision is traceable; the audit log is a first-class feature, not a footnote.
- **Calm by default** — use colour sparingly; only red/amber for genuine alerts.

---

## 3. Design Tokens

### Colour Palette

| Token | Hex | Usage |
|---|---|---|
| `--color-bg` | `#0F1117` | Page background |
| `--color-surface` | `#1A1D27` | Cards, panels, sidebars |
| `--color-surface-raised` | `#22263A` | Modals, dropdowns |
| `--color-border` | `#2E3248` | Dividers, card borders |
| `--color-primary` | `#6C63FF` | Primary CTAs, links, active states |
| `--color-primary-hover` | `#5A52E0` | Primary button hover |
| `--color-success` | `#22C55E` | Confidence > 0.85, task done, health good |
| `--color-warning` | `#F59E0B` | Confidence 0.65–0.85, in-progress, warnings |
| `--color-danger` | `#EF4444` | Confidence < 0.65, blocked, escalation alerts |
| `--color-text-primary` | `#F1F5F9` | Headings, primary body text |
| `--color-text-secondary` | `#94A3B8` | Captions, metadata, labels |
| `--color-text-muted` | `#475569` | Placeholders, disabled states |

### Typography

| Token | Value | Usage |
|---|---|---|
| `--font-family` | `Inter, sans-serif` | All UI text |
| `--font-size-xs` | `11px` | Badges, metadata |
| `--font-size-sm` | `13px` | Labels, captions |
| `--font-size-base` | `15px` | Body text |
| `--font-size-md` | `17px` | Card titles, section headers |
| `--font-size-lg` | `22px` | Page titles |
| `--font-size-xl` | `30px` | Hero stats, KPI numbers |
| `--font-weight-normal` | `400` | Body |
| `--font-weight-medium` | `500` | Labels, nav items |
| `--font-weight-semibold` | `600` | Card titles, CTAs |
| `--font-weight-bold` | `700` | Page headings, KPI numbers |

### Spacing Scale

| Token | Value |
|---|---|
| `--space-1` | `4px` |
| `--space-2` | `8px` |
| `--space-3` | `12px` |
| `--space-4` | `16px` |
| `--space-5` | `20px` |
| `--space-6` | `24px` |
| `--space-8` | `32px` |
| `--space-10` | `40px` |
| `--space-12` | `48px` |

### Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `6px` | Badges, chips |
| `--radius-md` | `10px` | Cards, inputs |
| `--radius-lg` | `16px` | Modals, panels |
| `--radius-full` | `9999px` | Avatars, pill tags |

### Shadows

| Token | Value |
|---|---|
| `--shadow-card` | `0 2px 12px rgba(0,0,0,0.35)` |
| `--shadow-modal` | `0 8px 40px rgba(0,0,0,0.6)` |
| `--shadow-dropdown` | `0 4px 20px rgba(0,0,0,0.4)` |

---

## 4. Layout & Navigation

### App Shell

```
┌─────────────────────────────────────────────────────┐
│  SIDEBAR (240px fixed)  │  MAIN CONTENT AREA        │
│                         │                           │
│  Logo: Tech Sarathi     │  Topbar (56px):           │
│                         │  [Page Title] [Search]    │
│  Nav Items:             │  [Notifications] [Avatar] │
│  - Dashboard            │                           │
│  - Projects             │  Page content scrolls     │
│  - Escalations  (badge) │  here                     │
│  - Audit Log            │                           │
│  - Team                 │                           │
│                         │                           │
│  ─────────────          │                           │
│  User avatar + name     │                           │
│  Settings               │                           │
└─────────────────────────────────────────────────────┘
```

### Sidebar Specs
- Width: `240px`, fixed, dark background `--color-surface`
- Logo at top: `Tech Sarathi` wordmark + icon, `32px` height
- Nav items: `44px` height, `16px` horizontal padding, `--font-size-sm`, `--font-weight-medium`
- Active state: `--color-primary` left border `3px`, background tint
- Escalation nav item: shows a red badge with pending count
- Bottom section: user avatar (32px circle), display name, Settings icon

### Topbar Specs
- Height: `56px`, `--color-surface`, bottom border `--color-border`
- Left: page title `--font-size-md --font-weight-semibold`
- Right: global search input, notification bell (badge), user avatar

---

## 5. Pages & Screens

---

### Screen 1 — Dashboard

**Route:** `/dashboard`
**File:** `src/components/Dashboard.jsx`

#### Purpose
The PM's home base. Shows all active projects at a glance with health indicators and the most urgent escalation.

#### Layout

```
┌──────────────────────────────────────────────────────┐
│  KPI Strip (4 stats across full width)               │
│  [Active Projects] [Escalations Pending]             │
│  [Avg Confidence]  [Tasks Overdue]                   │
├──────────────────────────────────────────────────────┤
│  Section Header: "Active Projects"  [+ New Project]  │
│                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ Project Card │ │ Project Card │ │ Project Card │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ │
│                                                      │
│  (cards wrap to next row as needed)                  │
├──────────────────────────────────────────────────────┤
│  Section Header: "Needs Your Attention"              │
│  [Top 3 escalation items — inline cards]             │
└──────────────────────────────────────────────────────┘
```

#### KPI Strip Component
- 4 equal-width stat cards in a horizontal row
- Each card: large number (`--font-size-xl --font-weight-bold`), label below (`--font-size-sm --color-text-secondary`)
- "Escalations Pending" number uses `--color-danger` if > 0
- "Avg Confidence" number uses confidence colour logic (green / amber / red)

#### Project Card Component
- Width: `~320px`, grid layout (3 columns on 1440px, 2 on 1024px)
- Background: `--color-surface`, border: `1px solid --color-border`, radius: `--radius-md`
- **Health indicator strip**: 4px top border, colour driven by confidence score
  - Green (`--color-success`) for confidence > 0.85
  - Amber (`--color-warning`) for 0.65 – 0.85
  - Red (`--color-danger`) for < 0.65
- Card content:
  - Project name (`--font-size-md --font-weight-semibold`)
  - Priority badge (pill tag: Critical / High / Medium / Low with matching colour)
  - Progress bar: percentage complete, `--color-primary` fill
  - Deadline: calendar icon + date, turns `--color-danger` if < 3 days away
  - Confidence score: circular gauge or pill — `0.87` in matching colour
  - Footer: PM avatar + name, task count `12 tasks`
- Hover: subtle border brightens, `cursor: pointer`, navigate to Project Detail

#### New Project Button
- Placement: top-right of "Active Projects" section header
- Style: filled `--color-primary`, `--font-weight-semibold`, `--radius-sm`
- Opens a slide-over panel (not a full page navigation)

---

### Screen 2 — Project Detail

**Route:** `/projects/:id`
**File:** `src/components/ProjectDetail.jsx`

#### Purpose
Full detail view for a single project. Task board, risk sidebar, team panel, and confidence timeline.

#### Layout

```
┌──────────────────────────────────────────────────────┐
│  Breadcrumb: Dashboard > [Project Name]              │
│  Page Title + Priority Badge + Status Chip           │
│  Deadline | PM Name | Confidence Score (large)       │
├────────────────────────────┬─────────────────────────┤
│  TASK BOARD (Kanban)       │  RIGHT SIDEBAR (320px)  │
│                            │                         │
│  [Todo] [In Progress]      │  Risk Panel             │
│  [Blocked] [Done]          │  ─────────────          │
│                            │  Risk flag cards        │
│  Task cards in each column │  (from Risk Agent)      │
│                            │                         │
│                            │  ─────────────          │
│                            │  Team Panel             │
│                            │  Assignee + load bar    │
│                            │                         │
│                            │  ─────────────          │
│                            │  Confidence Timeline    │
│                            │  (sparkline chart)      │
└────────────────────────────┴─────────────────────────┘
```

#### Kanban Board
- 4 columns: `Todo` | `In Progress` | `Blocked` | `Done`
- Column header: title + task count badge
- `Blocked` column header uses `--color-danger`
- Task Card:
  - Title (`--font-size-sm --font-weight-medium`)
  - Assignee avatar (24px) + name
  - Due date chip — red if overdue
  - Risk score dot indicator (coloured circle, 8px)
  - Estimated hours badge
  - Drag-and-drop to move between columns

#### Risk Panel (Right Sidebar)
- Header: "Risk Flags" + count badge in red
- Each risk flag card:
  - Icon (warning triangle) in `--color-danger` or `--color-warning`
  - Short description of the risk
  - Affected task name (link to task)
  - Risk score pill

#### Team Panel (Right Sidebar)
- Header: "Team Capacity"
- Each member row:
  - Avatar (28px) + name
  - Capacity bar: `current_load / availability`, colour shifts amber > 70%, red > 90%
  - Hours label: `28 / 40 hrs`

#### Confidence Timeline (Right Sidebar)
- Small sparkline chart (recharts `LineChart`)
- X-axis: date, Y-axis: 0.0 – 1.0
- Horizontal reference lines at 0.65 (red dashed) and 0.85 (green dashed)
- Tooltip on hover showing score + date

---

### Screen 3 — Escalation Queue

**Route:** `/escalations`
**File:** `src/components/EscalationQueue.jsx`

#### Purpose
The human review inbox. PMs see all decisions the AI was not confident enough to make autonomously and can approve, reject, or override them.

#### Layout

```
┌──────────────────────────────────────────────────────┐
│  Page Title: "Escalation Queue"   [Pending: 5 badge] │
│  Filter bar: [All | Staffing | Risk | Planning]      │
│              [Project dropdown] [Date range]         │
├──────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────┐  │
│  │ Escalation Card                                │  │
│  │ Agent badge | Project name | Confidence score  │  │
│  │ Reasoning text (2–3 lines)                     │  │
│  │ Suggested action (indented block)              │  │
│  │ [Approve]  [Reject]  [Override]  [View Detail] │  │
│  └────────────────────────────────────────────────┘  │
│  (list continues...)                                 │
└──────────────────────────────────────────────────────┘
```

#### Escalation Card
- Background: `--color-surface`, left border `4px --color-danger`
- Top row:
  - Agent badge (pill): e.g. `Staffing Agent` in `--color-primary` tint
  - Project name (link)
  - Confidence score pill: e.g. `0.52` in `--color-danger`
  - Timestamp (relative): `2 hours ago`
- Reasoning block: `--font-size-sm --color-text-secondary`, max 3 lines with "Show more"
- Suggested action block: light tinted background `--color-surface-raised`, monospace-style text
- Action buttons:
  - `Approve` — filled green (`--color-success`)
  - `Reject` — outlined red (`--color-danger`)
  - `Override` — outlined `--color-primary`
  - `View Detail` — text link
- On approval/rejection: card animates out, count badge decrements

#### Empty State
- Centered illustration + text: "All caught up — no pending escalations."
- Subtext in `--color-text-secondary`

---

### Screen 4 — Audit Log

**Route:** `/audit`
**File:** `src/components/AuditLog.jsx`

#### Purpose
A filterable, exportable timeline of every automated decision made by the AI agents.

#### Layout

```
┌──────────────────────────────────────────────────────┐
│  Page Title: "Audit Log"              [Export CSV]   │
│  Filter bar:                                         │
│  [Agent ▼] [Project ▼] [Date Range] [Confidence ▼]  │
├──────────────────────────────────────────────────────┤
│  Timeline list (reverse chronological)               │
│                                                      │
│  ● [timestamp]  [Agent Badge]  [Action]              │
│    Project: X  |  Task: Y  |  Confidence: 0.91       │
│    Input summary →  Output summary                   │
│    [Expand for full JSON]                            │
│                                                      │
│  ● [timestamp]  [Agent Badge]  [Action]              │
│    ...                                               │
│                                                      │
│  [Load more]                                         │
└──────────────────────────────────────────────────────┘
```

#### Audit Row
- Left: coloured dot (colour = confidence level), vertical connector line between rows
- Agent badge: pill with agent name, each agent has a unique tint colour
- Action text: e.g. `Task assigned to Sahil Prajapati` (`--font-weight-medium`)
- Metadata row: project name, task name, confidence score, execution time in ms
- Expandable: click row to reveal full `input_data` and `output_data` JSON in a code block
- Human override rows: show a `Human Override` badge in amber

#### Filter Bar
- Agent multi-select dropdown
- Project searchable dropdown
- Date range picker (start / end)
- Confidence range slider (0.0 – 1.0)
- Active filters shown as dismissible chips below the bar

#### Export Button
- Top-right, outlined style
- Downloads filtered results as `audit_log_export.csv`

---

### Screen 5 — Team Panel

**Route:** `/team`
**File:** `src/components/TeamPanel.jsx`

#### Purpose
Overview of all team members, their skills, current workload, and assignment history.

#### Layout

```
┌──────────────────────────────────────────────────────┐
│  Page Title: "Team"              [+ Add Member]      │
├──────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐    │
│  │  Member Row                                  │    │
│  │  [Avatar] [Name + Role]  [Skills chips]      │    │
│  │  Capacity bar ████████░░ 32/40 hrs           │    │
│  │  Active tasks: 4    [View Tasks]             │    │
│  └──────────────────────────────────────────────┘    │
│  (list continues...)                                 │
└──────────────────────────────────────────────────────┘
```

#### Member Row
- Avatar: 40px circle, initials fallback with random `--color-primary` tint background
- Name (`--font-weight-semibold`) + Role (`--color-text-secondary --font-size-sm`)
- Skills: pill chips, up to 4 visible + `+N more` overflow chip
- Capacity bar: full-width progress bar, colour thresholds:
  - Green (< 70%), Amber (70–90%), Red (> 90%)
- Active task count + "View Tasks" text link

---

## 6. Shared Components

### Confidence Badge
```
Props: score (float 0.0–1.0)
Renders: pill with score text, background tinted by threshold
  > 0.85 → green tint
  0.65–0.85 → amber tint
  < 0.65 → red tint
```

### Agent Badge
```
Props: agentName (string)
Renders: pill with agent name, unique colour per agent
  intake     → indigo
  planning   → blue
  staffing   → violet
  risk       → orange
  coordinator → teal
  communication → cyan
  escalation → red
```

### Status Chip
```
Props: status (string)
Values: todo | in_progress | blocked | done | active | paused | escalated | completed
Renders: small pill with matching colour and label
```

### Priority Badge
```
Props: priority (string)
Values: low | medium | high | critical
Renders: pill — low (grey), medium (blue), high (amber), critical (red)
```

### Capacity Bar
```
Props: current (int), max (int)
Renders: full-width bar, colour shifts green → amber → red by load %
Label: "current / max hrs"
```

### Empty State
```
Props: icon, title, subtitle, ctaLabel, ctaAction
Renders: centered layout — icon (48px), title, subtitle, optional CTA button
```

### Slide-Over Panel
```
Used for: New Project form, Task detail
Renders: panel slides in from right (400px wide), overlay backdrop
Close: X button or click outside
```

---

## 7. Forms

### New Project Form (Slide-Over)

Fields:
- Project Name — text input, required
- Description — textarea, 3 rows
- Priority — select: Low / Medium / High / Critical
- Deadline — date picker, must be future date
- Required Skills — multi-select tag input (searchable)
- Team Size — number input

Submit button: `Create Project` (primary filled)
On submit: triggers Intake Agent → Planning Agent pipeline, shows inline loading state.

### Add Task Form (inline in Kanban column)

Fields:
- Task Title — text input
- Description — textarea, 2 rows
- Estimated Hours — number input
- Due Date — date picker
- Assignee — searchable team member dropdown

---

## 8. States & Feedback

### Loading States
- Skeleton screens for cards and lists (not spinners)
- Agent pipeline progress: step-by-step indicator showing which agent is currently running
  ```
  [✓ Intake] → [✓ Planning] → [⟳ Staffing] → [· Risk] → [· Coordinator]
  ```

### Toast Notifications
- Position: bottom-right
- Types: success (green), warning (amber), error (red), info (blue)
- Auto-dismiss: 4 seconds
- Examples:
  - `Project "Mobile App" created — confidence 0.91 ✓`
  - `Escalation from Staffing Agent — review required ⚠`
  - `Task assigned to Amit Yadav automatically ✓`

### Confirmation Dialogs
- Used for: Reject escalation, Delete project, Override decision
- Modal (not toast): title, description, destructive action button in red, cancel button

### Error States
- Inline field validation errors below inputs in `--color-danger --font-size-xs`
- API errors: full-width error banner below topbar, dismissible

---

## 9. Responsive Behaviour

| Breakpoint | Layout Adjustment |
|---|---|
| `≥ 1440px` | 3-column project card grid, sidebar always visible |
| `1024px – 1439px` | 2-column project card grid, sidebar always visible |
| `768px – 1023px` | 1-column layout, sidebar collapses to icon-only (48px) |
| `< 768px` | Mobile: sidebar becomes bottom nav, all panels go full-screen |

---

## 10. Iconography

- Icon library: **Lucide React** (`lucide-react`)
- Size: `16px` inline, `20px` standalone, `24px` nav items
- Stroke width: `1.5px` default
- Key icons in use:

| Usage | Icon Name |
|---|---|
| Dashboard | `LayoutDashboard` |
| Projects | `FolderKanban` |
| Escalations | `AlertTriangle` |
| Audit Log | `ScrollText` |
| Team | `Users` |
| Risk | `ShieldAlert` |
| Confidence | `Gauge` |
| Approve | `CheckCircle` |
| Reject | `XCircle` |
| Override | `Pencil` |
| New Project | `Plus` |
| Export | `Download` |
| Settings | `Settings` |
| Notifications | `Bell` |

---

## 11. Animations & Transitions

- Page transitions: `opacity 0 → 1`, `150ms ease`
- Card hover: `transform translateY(-2px)`, `200ms ease`
- Slide-over: slides in from right, `300ms cubic-bezier(0.4, 0, 0.2, 1)`
- Escalation card dismiss: fade + slide left, `250ms ease`
- Kanban drag: drop shadow on drag, opacity 0.7 while dragging
- Toast enter/exit: slide up from bottom, `200ms ease`

---

## 12. Accessibility

- All interactive elements have `aria-label` or visible label
- Focus rings: `2px solid --color-primary`, `2px offset`
- Colour is never the sole indicator — all health states have an icon + text alongside colour
- Confidence badges include `aria-label="Confidence score: 0.87"`
- Keyboard navigable: sidebar, kanban board, escalation queue
- Minimum contrast ratio: 4.5:1 for all body text

---

*Design specification for Tech Sarathi | Input for Snitch.ai UI/UX generation | NIRMAN Hackathon — Amity University Mumbai | April 2026*
