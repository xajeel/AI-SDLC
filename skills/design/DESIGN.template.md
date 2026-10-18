---
version: alpha
name: <product>
description: "<who it serves and how it feels, one line>. Source: designed <YYYY-MM-DD> | extracted from code <YYYY-MM-DD>"
colors:                  # 4–6 roles, #RRGGBB; a component below uses each one
  primary: "<hex>"       # the main action
  on-primary: "<hex>"    # text and icons on primary, ≥ 4.5:1
  surface: "<hex>"       # page and card background
  on-surface: "<hex>"    # body text, ≥ 4.5:1 on surface
  muted: "<hex>"         # secondary text and borders
  danger: "<hex>"        # errors and destructive actions
typography:              # fontSize in rem; lineHeight unitless
  display:
    fontFamily: <family>
    fontSize: <rem>
    fontWeight: <n>
    lineHeight: <n>
  heading:
    fontFamily: <family>
    fontSize: <rem>
    fontWeight: <n>
    lineHeight: <n>
  body:
    fontFamily: <family>
    fontSize: <rem>
    fontWeight: <n>
    lineHeight: <n>
  label:
    fontFamily: <family>
    fontSize: <rem>
    fontWeight: <n>
    lineHeight: <n>
rounded:
  sm: <px>
  md: <px>
  full: 9999px
spacing:
  xs: <px>
  sm: <px>
  md: <px>
  lg: <px>
  xl: <px>
components:              # variants are separate entries: <name>-hover, <name>-disabled
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
    height: 44px
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    height: 44px
  hint-text:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
  error-text:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.danger}"
---

# <product> — design

<!-- Prose is in STE (../plan/ste.md): short sentences, active voice, one rule per sentence. Keep the section order. Values live in the YAML above; prose says when and why to use them. -->

## Overview
<!-- The users, the main job, the ambition (persuade | operate | be read | be experienced), the feel in three words, the signature element. -->

## Colors
<!-- One line per token: when to use it and when not to. The text and background pairs that pass contrast. -->

## Typography
<!-- The role of each style. Reading text: 45–80 characters per line. -->

## Layout
<!-- Breakpoints (375 / 768 / 1440), max content width, grid, the spacing rhythm. -->

## Elevation & Depth
<!-- How layers separate: border, tone, or shadow. Write each shadow value here; /build uses no other. -->

## Shapes
<!-- Radius per element type. Icon set and stroke width. -->

## Components
<!-- Per component: the file that implements it [read path:line], its states (default, hover, focus, disabled, loading, error), and its focus style. -->

## Do's and Don'ts
<!-- Rules /build follows and /qa checks. Motion durations and the reduced-motion rule. Each common default kept, with its reason. Extracted files: stray values and the files that use them (debt). -->
