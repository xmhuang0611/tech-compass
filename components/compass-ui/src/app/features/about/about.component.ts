import { Component } from "@angular/core";
import { siteConfig } from "../../core/config/site.config";

interface TeamMember {
  name: string;
  role: string;
  avatar: string;
  bio: string;
  url?: string;
}

interface Feature {
  icon: string;
  title: string;
  description: string;
  url?: string;
}

interface AboutConfig {
  hero: {
    title: string;
    subtitle: string;
  };
  team: {
    title: string;
    members: TeamMember[];
  };
  features: {
    title: string;
    items: Feature[];
  };
  engagement: {
    title: string;
    cards: Array<{
      icon: string;
      title: string;
      description: string;
      url?: string;
    }>;
  };
}

@Component({
  selector: "tc-about",
  templateUrl: "./about.component.html",
  styleUrls: ["./about.component.scss"],
})
export class AboutComponent {
  aboutConfig: AboutConfig = siteConfig.about;
  window = window;
}
