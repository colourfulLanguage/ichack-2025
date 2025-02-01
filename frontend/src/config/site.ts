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
    github: "https://github.com/frontio-ai/heroui",
    twitter: "https://twitter.com/hero_ui",
    discord: "https://discord.gg/9b6yyZKmH4",
    sponsor: "https://patreon.com/jrgarciadev",
  },
};
