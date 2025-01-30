export const siteConfig = {
  // Basic site info
  name: 'Tech Compass',
  logo: {
    path: 'assets/logo.svg',
    alt: 'Tech Compass Logo'
  },
  favicon: {
    svg: 'assets/favicon.svg',
    png: 'assets/favicon.png'
  },

  // Home page hero section
  hero: {
    title: 'Tech Compass',
    subtitle: 'Your guide to technology solutions',
    searchPlaceholder: 'Search solutions...'
  },

  // Intro section
  intro: {
    items: [
      {
        icon: 'pi pi-compass',
        title: 'Technology Navigation',
        description: 'Navigate through the complex technology landscape with confidence. Find the right solutions that match your team\'s needs.'
      },
      {
        icon: 'pi pi-check-circle',
        title: 'Informed Decisions',
        description: 'Make data-driven technology decisions with comprehensive evaluations, real user feedback, and expert recommendations.'
      },
      {
        icon: 'pi pi-users',
        title: 'Team Alignment',
        description: 'Keep your teams aligned on technology choices. Share knowledge and best practices across departments.'
      }
    ]
  },

  // Benefits section
  benefits: {
    title: 'Why Tech Compass?',
    image: 'assets/tech-radar.svg',
    items: [
      {
        icon: 'pi pi-chart-line',
        text: 'Track and evaluate technology trends in your organization'
      },
      {
        icon: 'pi pi-shield',
        text: 'Make informed decisions about adopting or retiring technologies'
      },
      {
        icon: 'pi pi-sync',
        text: 'Stay updated with recommendations and best practices'
      },
      {
        icon: 'pi pi-sitemap',
        text: 'Understand technology dependencies and relationships'
      }
    ]
  },

  // Testimonials section
  testimonials: {
    title: 'Trusted by Tech Leaders',
    items: [
      {
        quote: 'Tech Compass has transformed how we make technology decisions. It\'s now easier to align our tech stack across different teams and projects.',
        author: {
          name: 'Sarah Chen',
          title: 'Chief Technology Officer',
          company: 'Enterprise Software Company',
          avatar: 'assets/avatars/avatar1.svg'
        }
      },
      {
        quote: 'The ability to track and evaluate technology trends has helped us make more informed decisions about our tech investments.',
        author: {
          name: 'Michael Rodriguez',
          title: 'VP of Engineering',
          company: 'Cloud Services Provider',
          avatar: 'assets/avatars/avatar2.svg'
        }
      },
      {
        quote: 'Having a centralized platform for technology recommendations has significantly improved our development team\'s productivity.',
        author: {
          name: 'Emily Watson',
          title: 'Head of Architecture',
          company: 'Financial Technology Firm',
          avatar: 'assets/avatars/avatar3.svg'
        }
      }
    ]
  },

  // Footer content
  footer: {
    aboutText: 'Tech Compass - Your Technology Solutions Library',
    quickLinks: [
      { label: 'Home', path: '/' },
      { label: 'Solution Catalog', path: '/solution-catalog' },
      { label: 'About', path: '/about' }
    ],
    copyright: '© 2024 Tech Compass'
  }
}; 