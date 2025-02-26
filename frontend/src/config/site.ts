export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "Vite + HeroUI",
  description: "Bluree",
  navItems: [
    {
      label: "Upload",
      href: "/",
    },
    {
      label: "Confirm",
      href: "/confirm",
    },
    {
      label: "Check",
      href: "/check",
    },
    {
      label: "Process",
      href: "/process",
    },
    {
      label: "Results",
      href: "/results",
    },
    {
      label: "About",
      href: "/about",
    },
  ],
  navMenuItems: [],
  links: {
    github: "https://github.com/colourfulLanguage/ichack-2025",
  },
};
