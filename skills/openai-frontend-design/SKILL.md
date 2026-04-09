---
name: openai-frontend-design
description: Use when the task asks for a visually strong landing page, website, app, prototype, demo, or game UI. This skill enforces restrained composition, image-led hierarchy, cohesive content structure, and tasteful motion while avoiding generic cards, weak branding, and UI clutter. Enhanced with Claude's dimensional aesthetic guidance.
---

# OpenAI Frontend Design Skill (Enhanced Edition)

Use this skill when the quality of the work depends on art direction, hierarchy, restraint, imagery, and motion rather than component count.

Goal: ship interfaces that feel deliberate, premium, and current. Default toward award-level composition: one big idea, strong imagery, sparse copy, rigorous spacing, and a small number of memorable motions.

## Working Model

Before building, write three things:

- **visual thesis**: one sentence describing mood, material, and energy
- **content plan**: hero, support, detail, final CTA
- **interaction thesis**: 2-3 motion ideas that change the feel of the page

Each section gets one job, one dominant visual idea, and one primary takeaway or action.

## Hard Rules (Negative Constraints) ⭐ ENHANCED

### Absolute Prohibitions:
- ❌ **No cards by default** - Cards only as user interaction containers
- ❌ **No hero cards by default** - Full-bleed only
- ❌ **No boxed or center-column hero** - Edge-to-edge required
- ❌ **No more than one dominant idea per section**
- ❌ **No section should need many tiny UI devices to explain itself**
- ❌ **No headline should overpower the brand on branded pages**
- ❌ **No filler copy** - Apply 30% deletion test
- ❌ **No split-screen hero unless text sits on a calm, unified side**
- ❌ **No more than two typefaces without a clear reason**
- ❌ **No more than one accent color unless the product already has a strong system**

### Font & Color Constraints ⭐ NEW:
- ❌ **Forbidden fonts**: Inter, Roboto, Open Sans, Lato, Arial, system defaults
- ❌ **Forbidden defaults**: Purple-on-white, blue-purple gradients
- ✅ **Required**: Expressive, purposeful fonts
- ✅ **Required**: Clear CSS variable system

### Anti-Card Test:
> If removing borders, shadows, background colors, or rounded corners does not affect content understanding, do not use card wrapping.

## Beautiful Defaults

- Start with composition, not components.
- Prefer a full-bleed hero or full-canvas visual anchor.
- Make the brand or product name the loudest text.
- Keep copy short enough to scan in seconds.
- Use whitespace, alignment, scale, cropping, and contrast before adding chrome.
- Limit the system: two typefaces max, one accent color by default.
- Default to cardless layouts. Use sections, columns, dividers, lists, and media blocks instead.
- Treat the first viewport as a poster, not a document.

## Landing Pages

Default sequence (ENFORCED):

1. **Hero**: brand or product, promise, CTA, and one dominant visual
2. **Support**: one concrete feature, offer, or proof point
3. **Detail**: atmosphere, workflow, product depth, or story
4. **Final CTA**: convert, start, visit, or contact

### Hero Rules ⭐ STRICT:

**Allowed Elements (5 only)**:
1. Brand identifier
2. Main headline (H1)
3. One supporting sentence
4. CTA button group
5. One dominant visual

**Explicitly Forbidden**:
- ❌ Statistics numbers
- ❌ Schedule lists
- ❌ Address information
- ❌ Promo tags
- ❌ "Featured this week" sections
- ❌ Hero cards, stat strips, logo clouds, pill soup, floating dashboards

**Composition Rules**:
- One composition only
- Full-bleed image or dominant visual plane
- **Canonical full-bleed rule**: Hero must run edge-to-edge with no inherited page gutters, framed container, or shared max-width; constrain only the inner text/action column
- Brand first, headline second, body third, CTA fourth
- Keep headlines to roughly 2-3 lines on desktop and readable in one glance on mobile
- Keep the text column narrow and anchored to a calm area of the image
- All text over imagery must maintain strong contrast and clear tap targets

**Viewport Budget**:
- If the first screen includes a sticky/fixed header, that header counts against the hero
- The combined header + hero content must fit within the initial viewport
- When using `100vh`/`100svh` heroes, subtract persistent UI chrome or overlay the header

## Copy Strategy ⭐ ENHANCED

### Product Language vs Design Commentary:

**Product Language (REQUIRED)**:
- ✅ Specific, functional
- ✅ Action-oriented
- ✅ Concrete benefits

**Design Commentary (FORBIDDEN)**:
- ❌ "We provide powerful features"
- ❌ "Unlock your potential"
- ❌ Abstract, descriptive language

### 30% Deletion Test ⭐ NEW:
> If deleting 30 percent of the copy improves the page, keep deleting.

### Utility Copy for Product UI ⭐ NEW:

When the work is a dashboard, app surface, admin tool, or operational workspace, default to utility copy over marketing copy.

**Priority**:
- ✅ Orientation, status, action
- ❌ Promise, mood, brand voice

**Good Examples**:
- ✅ "Selected KPIs"
- ✅ "Plan status"
- ✅ "Search metrics"
- ✅ "Top segments"
- ✅ "Last sync"

**Bad Examples**:
- ❌ "Unlock your potential"
- ❌ "Transform your workflow"
- ❌ "Empower your team"

**Requirements**:
- Start with the working surface itself: KPIs, charts, filters, tables, status, or task context
- Section headings should say what the area is or what the user can do there
- Supporting text should explain scope, behavior, freshness, or decision value in one sentence
- If a sentence could appear in a homepage hero or ad, rewrite it until it sounds like product UI
- If a section does not help someone operate, monitor, or decide, remove it
- **Litmus check**: If an operator scans only headings, labels, and numbers, can they understand the page immediately?

## Typography (Claude-Inspired) ⭐ NEW

### Font Selection - Contrast Maximization:

**Explicitly Excluded**:
- ❌ Inter, Roboto, Open Sans, Lato, system default fonts

**Recommended Categories**:

#### Code Aesthetic:
- JetBrains Mono
- Fira Code
- Space Grotesk

#### Editorial Style:
- Playfair Display
- Crimson Pro

#### Technical Feel:
- IBM Plex family
- Source Sans 3

#### Distinctive:
- Bricolage Grotesque
- Newsreader

### Technical Constraints:
- **Extreme weight contrast**: 100/200 vs 800/900 (not 400 vs 600)
- **Size jumping**: 3x+ differences (not 1.5x)
- **High contrast pairing**: Display + Monospace OR Serif + Geometric Sans

## Themes (Claude-Inspired) ⭐ NEW

### Atmospheric Design Systems:

**RPG Theme Example**:
- **Colors**: Rich, dramatic fantasy tones
- **Materials**: Parchment textures, leather-bound styling, weathered materials
- **Decorations**: Ornate borders and decorative frame elements
- **Lighting**: Dramatic lighting effects
- **Typography**: Medieval-inspired serif typography

**Usage**: Allow models to autonomously derive specific CSS implementations based on internal understanding of aesthetic styles, rather than relying on hardcoded hex values.

## Backgrounds & Motion ⭐ ENHANCED

### Backgrounds:
- ✅ **Atmospheric backgrounds** - Subtle textures, gradients, contextual images
- ❌ Flat color fills

### Motion Requirements:
Ship at least 2-3 intentional motions for visually led work:
- One entrance sequence in the hero
- One scroll-linked, sticky, or depth effect
- One hover, reveal, or layout transition that sharpens affordance

**Motion Rules**:
- Noticeable in a quick recording
- Smooth on mobile
- Fast and restrained
- Consistent across the page
- Removed if ornamental only
- **Functional hierarchy creation, NOT noise-based decoration**

## Apps

Default to Linear-style restraint:

- Calm surface hierarchy
- Strong typography and spacing
- Few colors
- Dense but readable information
- Minimal chrome
- Cards only when the card is the interaction

For app UI, organize around:
- Primary workspace
- Navigation
- Secondary context or inspector
- One clear accent for action or state

**Avoid**:
- Dashboard-card mosaics
- Thick borders on every region
- Decorative gradients behind routine product UI
- Multiple competing accent colors
- Ornamental icons that do not improve scanning

If a panel can become plain layout without losing meaning, remove the card treatment.

## Imagery

Imagery must do narrative work.

- Use at least one strong, real-looking image for brands, venues, editorial pages, and lifestyle products.
- Prefer in-situ photography over abstract gradients or fake 3D objects.
- Choose or crop images with a stable tonal area for text.
- Do not use images with embedded signage, logos, or typographic clutter fighting the UI.
- Do not generate images with built-in UI frames, splits, cards, or panels.
- If multiple moments are needed, use multiple images, not one collage.

The first viewport needs a real visual anchor. Decorative texture is not enough.

## One-Job-Per-Section Principle ⭐ NEW

Each section must follow:
- **One headline**
- **One supporting sentence**
- **One core action**

This combats the model tendency to stack multiple marketing points in the same block.

## Technical Implementation

### Preferred Stack:
- **React + Tailwind + Framer Motion**

### React Patterns:
- **Prioritize**: useEffectEvent, startTransition, useDeferredValue
- **Forbidden**: Default useMemo/useCallback (follow React Compiler guide instead)

### Validation:
- Playwright automation testing required
- Verify multi-viewport rendering
- Verify interaction states

## Reject These Failures

- Generic SaaS card grid as the first impression
- Beautiful image with weak brand presence
- Strong headline with no clear action
- Busy imagery behind text
- Sections that repeat the same mood statement
- Carousel with no narrative purpose
- App UI made of stacked cards instead of layout
- Inter font usage
- Purple-on-white defaults
- Blue-purple gradients

## Litmus Checks

- Is the brand or product unmistakable in the first screen?
- Is there one strong visual anchor?
- Can the page be understood by scanning headlines only?
- Does each section have one job?
- Are cards actually necessary?
- Does motion improve hierarchy or atmosphere?
- Would the design still feel premium if all decorative shadows were removed?
- **NEW**: Does the page use atmospheric backgrounds instead of flat colors?
- **NEW**: Does the typography use extreme contrast (100/200 vs 800/900)?
- **NEW**: Does the copy pass the 30% deletion test?
- **NEW**: For product UI: Can an operator understand the page by scanning only headings, labels, and numbers?

## Summary of Enhancements

This enhanced edition combines:
- **OpenAI's negative constraints** - 15+ hard rules
- **Claude's dimensional guidance** - Typography, themes, backgrounds
- **Strict copy strategy** - Product language, 30% deletion test, utility copy
- **One-job-per-section** - Single responsibility principle
- **Enhanced validation** - More comprehensive litmus checks

**Result**: More predictable, higher-quality frontend outputs that avoid "AI-generated" aesthetics while enabling rapid style exploration.
