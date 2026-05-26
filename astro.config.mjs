import sitemap from "@astrojs/sitemap";
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://www.wineandchord.com",
  base: "/mycr",
  output: "static",
  publicDir: "./public",
  integrations: [sitemap()],
  build: {
    format: "preserve",
  },
});
