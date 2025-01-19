## Overview

The Tech Compass Library (TCL) is a desktop-first web application designed to help teams discover, evaluate, and share technology solutions. The UI design emphasizes professionalism, clarity, and efficiency, targeting technical professionals in enterprise environments.

## Design Philosophy

### Look and Feel
- **Professional & Enterprise-Ready**: Clean, modern interface suitable for business environments
- **Technology-Focused**: Visual elements that reflect technical sophistication
- **PrimeNG Integration**: Leveraging PrimeNG components for consistent enterprise-grade UI elements
- **Performance-Oriented**: Fast loading times and smooth transitions
- **Information Dense**: Efficient presentation of complex technical information

## Global Styles

### Color Palette

Primary Colors:
- Primary Blue: `#2563eb` (For primary actions, links)
- Secondary Blue: `#1e40af` (For hover states)
- Accent Blue: `#3b82f6` (For highlights, active states)

Neutral Colors:
- Background: `#ffffff` (Main content background)
- Surface: `#f8fafc` (Card backgrounds, secondary surfaces)
- Text Primary: `#1e293b` (Primary text)
- Text Secondary: `#64748b` (Secondary text, descriptions)

Status Colors:
- Success: `#10b981` (Positive states)
- Warning: `#f59e0b` (Warning states)
- Error: `#ef4444` (Error states)
- Info: `#3b82f6` (Information states)

### Typography

- **Primary Font**: Inter (Sans-serif)
- **Monospace Font**: JetBrains Mono (For code snippets)

Hierarchy:
- H1: 32px/40px, Weight: 600
- H2: 24px/32px, Weight: 600
- H3: 20px/28px, Weight: 600
- Body: 16px/24px, Weight: 400
- Small: 14px/20px, Weight: 400
- Caption: 12px/16px, Weight: 400

### Spacing System

Based on 4px grid:
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

### Shadows

- Card: `0 1px 3px rgba(0, 0, 0, 0.1)`
- Dropdown: `0 4px 6px -1px rgba(0, 0, 0, 0.1)`
- Modal: `0 20px 25px -5px rgba(0, 0, 0, 0.1)`

### Component Styles

- Border Radius: 6px (Consistent across all components)
- Button Heights: 40px (Standard), 36px (Compact)
- Input Heights: 40px
- Card Padding: 24px

## URL Structure

### Solution Pages
- Solution List: `/solutions`
- Solution Detail: `/solutions/{slug}`
  - Example: `/solutions/engineering-cloud-infrastructure-docker`
- Solution Edit: `/solutions/{slug}/edit`
- Solution Comments: `/solutions/{slug}/comments`
- Solution Ratings: `/solutions/{slug}/ratings`

### Category Pages
- Category List: `/categories`
- Category Detail: `/categories/{category-slug}`
  - Example: `/categories/container-platforms`

### Department Pages
- Department List: `/departments`
- Department Solutions: `/departments/{department-slug}`
  - Example: `/departments/engineering`

### Team Pages
- Team List: `/teams`
- Team Solutions: `/teams/{department-slug}/{team-slug}`
  - Example: `/teams/engineering/cloud-infrastructure`

## Navigation

### Breadcrumb Structure
- Solution Detail: `Home > {Department} > {Team} > {Solution Name}`
  - Example: `Home > Engineering > Cloud Infrastructure > Docker`
- Category View: `Home > Categories > {Category Name}`
- Department View: `Home > Departments > {Department Name}`
- Team View: `Home > Departments > {Department Name} > {Team Name}`

### URL Handling
- Slug Generation:
  - Lowercase all characters
  - Replace spaces and special characters with hyphens
  - Remove unnecessary words (a, an, the)
  - Maximum length: 100 characters
- Redirect Handling:
  - Preserve old slugs for redirection
  - 301 redirect from old slugs to new ones
  - Case-insensitive matching

### Search Integration
- Search results link directly to solution slugs
- Search suggestions show solution slugs
- Copy URL button on solution pages
- Share buttons use slug-based URLs

## Layout Designs

### Global Layout
- Fixed header with navigation
- Breadcrumb navigation below header
- Main content area with maximum width 1440px
- Responsive side margins (32px on desktop)

### Global Navigation

#### Header Bar
- Fixed position at top of viewport
- White background with subtle shadow
- Height: 64px
- Maximum width 1440px with responsive margins

#### Primary Navigation
- Left section:
  - Site logo (linked to home)
  - Primary navigation items:
    - Solutions Catalog
    - Categories
    - About
  - Search bar with autocomplete
    - Keyboard shortcut: Cmd/Ctrl + K
    - Search suggestions
    - Recent searches

- Right section:
  - User profile menu:
    - User avatar
    - Name display
    - Role/Department
    - Dropdown menu:
      - Profile settings
      - Preferences
      - Sign out
  - Notification bell:
    - Counter badge
    - Dropdown with recent notifications
    - Mark all as read option

#### Secondary Navigation
- Appears below header
- Light gray background (`#f1f5f9`)
- Height: 48px
- Contains:
  - Breadcrumb navigation
  - Context-specific actions
  - View toggles (grid/list)
  - Filter triggers

#### Mobile Considerations
- Collapsible menu for primary navigation
- Persistent search button
- Simplified user menu
- Full-width search overlay

#### Navigation States
- Active state: Primary color background
- Hover state: Light gray background
- Focus state: Blue outline
- Disabled state: Muted colors

#### Dropdown Menus
- Consistent width (240px)
- 8px rounded corners
- Drop shadow
- 8px padding
- Hover states on items
- Support for icons
- Support for dividers
- Support for nested menus

### Footer
- Full-width background with darker shade (`#1e293b`)
- Maximum width content area (1440px)
- Four-column layout:
  #### About Column
  - Site logo
  - Brief description
  - Social media links
  
  #### Quick Links
  - Home
  - Solutions Catalog
  - About Us
  - Support
  
  #### Support Info
  - Support team contact
  - Operating hours
  - Email address
  - Response time expectations
  
  #### Legal Links
  - Terms of Service
  - Privacy Policy
  - Cookie Policy
  - Accessibility Statement

- Bottom bar with:
  - Copyright notice
  - Version number
  - Last updated timestamp
- Responsive padding (32px on desktop)
- Light text on dark background
- Subtle hover effects on links

### Home Page

#### Hero Section
- Full-width background with subtle tech-themed pattern
- Large headline showcasing site tagline
- Sub-headline explaining platform value proposition
- Search bar prominently placed
- Quick action buttons for common tasks

#### Recommended Solutions
- Grid layout of solution cards (3 columns)
- Each card displays:
  - Solution logo/icon
  - Solution name
  - Brief description
  - Category badge
  - Rating indicator
  - Status badge

#### Popular Categories
- Horizontal scrollable list of category cards
- Visual icons representing each category
- Category name and solution count

### Tech Solutions Catalog Page

#### Filter Panel (Left Sidebar)
- Sticky position while scrolling
- Collapsible sections for:
  - Categories (Tree view)
  - Status filter
  - Department filter
  - Rating range
  - Tags (Multi-select with search)

#### Results Area
- Toggle between grid and list views
- Sorting options:
  - Name
  - Rating
  - Last updated
  - Most viewed
- Results per page selector
- Pagination controls

#### Solution Cards
- Consistent height and width
- Clear hierarchy of information
- Quick action buttons on hover
- Status indicators
- Rating display
- Tag chips

### Solution Detail Page

#### Header Section
- Solution name and logo
- Status badge
- Rating display
- Quick action buttons
- Share button

#### Content Layout
- Two-column layout for desktop
- Left column (70%):
  - Description
  - Features
  - Documentation
  - Use cases
- Right column (30%):
  - Key information card
  - Support contact
  - Related solutions

#### Information Display
- Tabbed interface for different sections
- Code snippet formatting
- Collapsible sections
- Progress indicators
- Version history timeline

### About Page

#### Hero Section
- Full-width banner with subtle tech pattern background
- Site logo prominently displayed
- Mission statement / tagline
- Brief introduction paragraph

#### Platform Overview
- Three-column grid highlighting key features
- Each feature card includes:
  - Icon representation
  - Feature title
  - Brief description
  - Visual indicator or statistic

#### Team Section
- Support team information
- Contact methods:
  - Email support
  - Team contact hours
  - Response time expectations

#### Platform Statistics
- Animated counters showing:
  - Total solutions cataloged
  - Active users
  - Departments using the platform
  - Total technology evaluations

#### Getting Started Guide
- Step-by-step cards showing:
  - How to search for solutions
  - How to evaluate technologies
  - How to contribute
  - How to get support
- Each step includes:
  - Step number
  - Illustrative icon
  - Clear instructions
  - Call-to-action button

#### FAQ Section
- Expandable accordion style questions
- Categorized questions
- Search functionality
- Links to related documentation

## Interactive Elements

### Buttons
- Primary: Filled background
- Secondary: Outlined
- Tertiary: Text only
- Icon buttons: Square with hover tooltip

### Forms
- Inline validation
- Helper text
- Error states
- Loading states
- Auto-complete where applicable

### Feedback
- Toast notifications
- Progress indicators
- Loading skeletons
- Empty states
- Error states

## Responsive Behavior
- Desktop-first design (minimum width: 1024px)
- Graceful scaling up to 4K displays
- Maintains readability on larger screens
- Optimized for common desktop resolutions:
  - 1920x1080
  - 1440x900
  - 2560x1440

## Accessibility
- WCAG 2.1 AA compliance
- High contrast ratios
- Keyboard navigation
- Screen reader support
- Focus indicators
- Alt text for images

## Design Tokens
```json
{
  "colors": {
    "primary": {
      "50": "#eff6ff",
      "500": "#2563eb",
      "700": "#1e40af"
    },
    "neutral": {
      "50": "#f8fafc",
      "900": "#1e293b"
    },
    "footer": {
      "background": "#1e293b",
      "text": "#f8fafc",
      "link": "#60a5fa",
      "linkHover": "#93c5fd",
      "border": "rgba(255, 255, 255, 0.1)"
    },
    "navigation": {
      "background": "#ffffff",
      "secondaryBackground": "#f1f5f9",
      "text": "#1e293b",
      "activeText": "#2563eb",
      "hoverBackground": "#f1f5f9",
      "shadow": "0 1px 3px rgba(0, 0, 0, 0.1)",
      "border": "#e2e8f0",
      "dropdown": {
        "background": "#ffffff",
        "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        "hoverBackground": "#f8fafc"
      }
    }
  },
  "typography": {
    "fontFamilies": {
      "primary": "Inter, sans-serif",
      "mono": "JetBrains Mono, monospace"
    },
    "fontSizes": {
      "h1": "32px",
      "body": "16px",
      "footer": "14px",
      "footerHeading": "16px",
      "navigation": {
        "primary": "16px",
        "secondary": "14px",
        "dropdown": "14px"
      }
    },
    "fontWeights": {
      "navigation": {
        "normal": "400",
        "active": "500"
      }
    }
  },
  "spacing": {
    "xs": "4px",
    "xl": "32px",
    "navigation": {
      "height": "64px",
      "secondaryHeight": "48px",
      "dropdownWidth": "240px",
      "dropdownPadding": "8px",
      "itemPadding": "12px"
    }
  }
}
```

## AI Design Tool Prompts

### Home Page
"Create a modern, professional desktop web interface for a technology solutions library. The design should feature a hero section with a search bar, followed by a grid of solution cards. Use a clean, minimalist style with blue as the primary color (#2563eb). Include a fixed header with navigation and ensure the layout is optimized for desktop viewing with a maximum width of 1440px."

### Catalog Page
"Design a desktop catalog page for browsing technology solutions. Include a left sidebar with filters, and a main content area with a grid of solution cards. The design should support both grid and list views, with sorting and pagination controls. Use a light, professional color scheme with the primary color #2563eb. The layout should be optimized for desktop screens starting at 1024px width."

### Detail Page
"Create a detailed view page for a technology solution using a two-column layout. The left column should contain tabs for different content sections, while the right column shows key information in a card format. Use a professional, technical aesthetic with the primary color #2563eb. Include a header section with the solution name, status, and rating. Design for desktop screens with a minimum width of 1024px."

### About Page
"Design a modern, informative about page for a technology solutions platform. Include a hero section with the platform's mission statement, followed by a three-column feature overview grid. Add sections for team information, platform statistics with animated counters, a step-by-step getting started guide, and an FAQ accordion. Use the primary color #2563eb and maintain a professional, enterprise feel. The design should be optimized for desktop viewing with clear information hierarchy and engaging visual elements."
