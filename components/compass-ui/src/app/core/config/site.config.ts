export const siteConfig = {
  // Basic site info
  name: "Tech Compass",
  logo: {
    path: "assets/logo.svg",
    alt: "Tech Compass Logo",
  },
  favicon: {
    svg: "assets/favicon.svg",
    png: "assets/favicon.png",
  },

  // Auth related
  auth: {
    signIn: {
      title: "Welcome Back!",
      subtitle: "Sign in to continue to Tech Compass",
      usernameLabel: "Username",
      usernamePlaceholder: "Enter your username",
      passwordLabel: "Password",
      passwordPlaceholder: "Enter your password",
      signInButton: "Sign In",
      cancelButton: "Cancel",
      errors: {
        emptyFields: "Please enter both username and password",
        defaultError: "Authentication failed. Please try again.",
        inactiveUser: "Your account is inactive. Please contact an administrator.",
      },
    },
  },

  // Home page hero section
  hero: {
    title: "Tech Compass",
    subtitle: "Your guide to technology solutions",
    searchPlaceholder: "Search solutions...",
  },

  // Intro section
  intro: {
    items: [
      {
        icon: "pi pi-compass",
        title: "Technology Navigation",
        description:
          "Navigate through the complex technology landscape with confidence. Find the right solutions that match your team's needs.",
      },
      {
        icon: "pi pi-check-circle",
        title: "Informed Decisions",
        description:
          "Make data-driven technology decisions with comprehensive evaluations, real user feedback, and expert recommendations.",
      },
      {
        icon: "pi pi-users",
        title: "Team Alignment",
        description:
          "Keep your teams aligned on technology choices. Share knowledge and best practices across departments.",
      },
    ],
  },

  // Benefits section
  benefits: {
    title: "Why Tech Compass?",
    image: "assets/tech-radar.svg",
    items: [
      {
        icon: "pi pi-chart-line",
        text: "Track and evaluate technology trends in your organization",
      },
      {
        icon: "pi pi-shield",
        text: "Make decisions about adopting or retiring technologies",
      },
      {
        icon: "pi pi-sync",
        text: "Stay updated with recommendations and best practices",
      },
      {
        icon: "pi pi-sitemap",
        text: "Understand technology dependencies and relationships",
      },
    ],
  },

  // Testimonials section
  testimonials: {
    title: "Trusted by Tech Leaders",
    items: [
      {
        quote:
          "Tech Compass has transformed how we make technology decisions. It's now easier to align our tech stack across different teams and projects.",
        author: {
          name: "Sarah Chen",
          title: "Chief Technology Officer",
          company: "Enterprise Software Company",
          avatar: "assets/avatars/avatar1.svg",
        },
      },
      {
        quote:
          "The ability to track and evaluate technology trends has helped us make more informed decisions about our tech investments.",
        author: {
          name: "Michael Rodriguez",
          title: "VP of Engineering",
          company: "Cloud Services Provider",
          avatar: "assets/avatars/avatar2.svg",
        },
      },
      {
        quote:
          "Having a centralized platform for technology recommendations has significantly improved our development team's productivity.",
        author: {
          name: "Emily Watson",
          title: "Head of Architecture",
          company: "Financial Technology Firm",
          avatar: "assets/avatars/avatar3.svg",
        },
      },
    ],
  },

  // Footer content
  footer: {
    aboutText: `**Tech Compass** - Your technology solutions library, visit our [GitHub repository](https://github.com/tobyqin/tech-compass) to learn more.`,
    quickLinks: [
      { label: "Home", path: "/" },
      { label: "Solution Catalog", path: "/solutions" },
      { label: "Submit Solution", path: "/solutions/new" },
      { label: "About", path: "/about" },
    ],
    copyright: " 2024 Tech Compass",
  },

  // About page configuration
  about: {
    hero: {
      title: "About Tech Compass",
      subtitle: "Your guide to technology solutions",
    },
    team: {
      title: "Our Sponsors",
      members: [
        {
          name: "John Smith",
          role: "Gold Sponsor",
          avatar: "assets/avatars/avatar1.svg",
          bio: "Supporting innovation and technological advancement.",
          url: "https://example.com/john-smith",
        },
        {
          name: "Sarah Chen",
          role: "Platinum Sponsor",
          avatar: "assets/avatars/avatar2.svg",
          bio: "Empowering next-generation technology solutions.",
        },
        {
          name: "Michael Johnson",
          role: "Gold Sponsor",
          avatar: "assets/avatars/avatar3.svg",
          bio: "Fostering technological growth and innovation.",
        },
        {
          name: "Emily Davis",
          role: "Silver Sponsor",
          avatar: "assets/avatars/avatar1.svg",
          bio: "Driving digital transformation initiatives.",
        },
        {
          name: "David Wilson",
          role: "Gold Sponsor",
          avatar: "assets/avatars/avatar2.svg",
          bio: "Accelerating technology adoption and growth.",
        },
        {
          name: "Lisa Zhang",
          role: "Platinum Sponsor",
          avatar: "assets/avatars/avatar3.svg",
          bio: "Supporting sustainable technology development.",
        },
        {
          name: "Robert Taylor",
          role: "Gold Sponsor",
          avatar: "assets/avatars/avatar1.svg",
          bio: "Enabling digital innovation and transformation.",
        },
        {
          name: "Anna Martinez",
          role: "Platinum Sponsor",
          avatar: "assets/avatars/avatar2.svg",
          bio: "Advancing technology solutions for the future.",
        },
      ],
    },
    features: {
      title: "Our Mission",
      items: [
        {
          icon: "pi pi-check-square",
          title: "Standardization",
          description:
            "Establish and promote standardized software development processes and practices to ensure consistency and quality across development teams.",
          url: "https://example.com/standardization",
        },
        {
          icon: "pi pi-sync",
          title: "Modernization",
          description:
            "Guide teams in adopting modern development tools and methodologies to enhance productivity and maintain competitive advantage.",
        },
        {
          icon: "pi pi-cog",
          title: "Automation",
          description:
            "Empower development teams with automated solutions and tools to streamline workflows and improve development efficiency.",
        },
      ],
    },
    engagement: {
      title: "Get Involved",
      cards: [
        {
          icon: "pi pi-check-circle",
          title: "Adopt to Standards",
          description:
            "Implement standardized practices and methodologies in your development process.",
          url: "https://example.com/adopt-standards",
        },
        {
          icon: "pi pi-cog",
          title: "Automate Delivery",
          description:
            "Streamline your development workflow with automated tools and processes.",
        },
        {
          icon: "pi pi-shield",
          title: "Apply Best Practices",
          description:
            "Follow industry-proven best practices to enhance code quality and maintainability.",
        },
        {
          icon: "pi pi-plus",
          title: "Submit Solutions",
          description:
            "Share your technology solutions and contribute to our growing knowledge base.",
        },
        {
          icon: "pi pi-star",
          title: "Rate Solutions",
          description:
            "Help others by rating solutions based on your experience and implementation.",
        },
        {
          icon: "pi pi-comments",
          title: "Provide Feedback",
          description:
            "Comment on solutions and share your experiences with the community.",
        },
      ],
    },
  },

  // Navigation menu
  navigation: [
    {
      label: "Home",
      icon: "pi pi-home",
      path: "/",
    },
    {
      label: "Categories",
      icon: "pi pi-folder",
      path: "/categories",
    },
    {
      label: "Solutions",
      icon: "pi pi-list",
      path: "/solutions",
    },
    {
      label: "Tech Radar",
      icon: "pi pi-wave-pulse",
      path: "/radar",
    },
    {
      label: "Useful Links",
      icon: "pi pi-link",
      items: [
        {
          label: "Documentation",
          icon: "pi pi-file",
          url: "https://docs.techcompass.com",
          target: "_blank",
        },
        {
          label: "Feedback Wall",
          icon: "pi pi-comments",
          url: "https://feedback.techcompass.com",
          target: "_blank",
        },
      ],
    },
    {
      label: "About",
      icon: "pi pi-info-circle",
      path: "/about",
    },
  ],

  techRadar: {
    title: "Tech Radar",
    faqs: [
      {
        title: "What is the Tech Radar?",
        content: `
The Tech Radar is a list of technologies, complemented by an assessment result, called *ring assignment*. 
We use four rings with the following semantics:

* **ADOPT** — Proven technologies recommended for wide use in production, with low risk.

* **TRIAL** — Technologies successfully used in projects with some limitations identified. Moderate risk.

* **ASSESS** — Promising technologies worth exploring through research and prototypes. Higher risk.

* **HOLD** — Technologies not recommended for new projects but can be maintained in existing ones.`,
      },

      {
        title: "What is the purpose?",
        content: `
The Tech Radar helps engineering teams choose the best technologies for new projects. It's a platform for sharing knowledge and experience about technologies that we recommend using. Inspired by ThoughtWorks, it tracks important changes in software development that our teams should consider.`,
      },
      {
        title: "How do we maintain it?",
        content: `
The Tech Radar is maintained by our *Principal Engineers* who lead technology discussions and ring assignments through proposals and voting. All Engineering teams can contribute by sharing their experiences and best practices.`,
      },
      {
        title: "How can I provide feedback?",
        content: `
We welcome and value your feedback on the Tech Radar! Here's how you can contribute:

* **Submit Ring Change Proposals** — If you believe a technology should be moved to a different ring, submit a proposal with your rationale and supporting evidence.

* **Report Issues** — Found incorrect information or have concerns about a technology's placement? Let us know through our issue tracking system.

You can submit your feedback through any of these channels:
* Create an issue in our [GitHub repository](https://github.com/your-org/tech-radar/issues)
* Email the Principal Engineers team at *tech-radar@your-company.com*

Your input helps keep the Tech Radar relevant and valuable for the entire engineering community.`,
      },
    ],
  },
};
