## Overview

The Tech Compass Library (TCL) is a desktop-first web application designed to help teams discover, evaluate, and share technology solutions. The UI design emphasizes professionalism, clarity, and efficiency, targeting technical professionals in enterprise environments.

## Tech stacks

- **[Angular](https://angular.dev)**

  - A platform for building mobile and desktop web applications

- **[PrimeNG](https://primeng.org)**
  - A rich set of open-source UI components for Angular applications
  - [Sakai Template](https://github.com/primefaces/sakai-ng) - Admin template

## Design Philosophy

### Look and Feel
- **Professional & Enterprise-Ready**: Clean, modern interface suitable for business environments
- **Technology-Focused**: Visual elements that reflect technical sophistication
- **PrimeNG Integration**: Leveraging PrimeNG components for consistent enterprise-grade UI elements
- **Performance-Oriented**: Fast loading times and smooth transitions
- **Information Dense**: Efficient presentation of complex technical information

## URL Structure

### Solution Pages
- Solution List: `/solutions`
- Solution Detail: `/solutions/{slug}`
  - Example: `/solutions/engineering-cloud-infrastructure-docker`

### Category Pages
- Category List: `/categories`
- Category Detail: `/categories/{category-name}`
  - Example: `/categories/container-platforms`

### Department Pages
- Department List: `/departments`
- Department Solutions: `/departments/{department-name}`
  - Example: `/departments/engineering`

## Navigation

### Breadcrumb Structure
- Solution Detail: `Home > {Category} > {Solution Name}`
  - Example: `Home > Container Platforms > Docker`
- Category View: `Home > Categories > {Category Name}`
- Department View: `Home > Departments > {Department Name}`

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
  
  #### Legal Links
  - Terms of Service
  - Privacy Policy

- Bottom bar with:
  - Copyright notice
  - Version number
  - Last updated timestamp
- Responsive padding
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

## AI Design Tool Prompts

### Home Page
"Create a modern, professional desktop web interface for a technology solutions library. The design should feature a hero section with a search bar, followed by a grid of solution cards. Use a clean, minimalist style with blue as the primary color (#2563eb). Include a fixed header with navigation and ensure the layout is optimized for desktop viewing with a maximum width of 1440px."

### Catalog Page
"Design a desktop catalog page for browsing technology solutions. Include a left sidebar with filters, and a main content area with a grid of solution cards. The design should support both grid and list views, with sorting and pagination controls. Use a light, professional color scheme with the primary color #2563eb. The layout should be optimized for desktop screens starting at 1024px width."

### Detail Page
"Create a detailed view page for a technology solution using a two-column layout. The left column should contain tabs for different content sections, while the right column shows key information in a card format. Use a professional, technical aesthetic with the primary color #2563eb. Include a header section with the solution name, status, and rating. Design for desktop screens with a minimum width of 1024px."

### About Page
"Design a modern, informative about page for a technology solutions platform. Include a hero section with the platform's mission statement, followed by a three-column feature overview grid. Add sections for team information, platform statistics with animated counters, a step-by-step getting started guide, and an FAQ accordion. Use the primary color #2563eb and maintain a professional, enterprise feel. The design should be optimized for desktop viewing with clear information hierarchy and engaging visual elements."
