import { NgModule } from "@angular/core";
import { RouterModule, Routes, TitleStrategy } from "@angular/router";
import { Title } from "@angular/platform-browser";
import { Injectable } from "@angular/core";
import { siteConfig } from "./core/config/site.config";
import { AuthGuard } from "./core/guards/auth.guard";

@Injectable()
class CustomTitleStrategy extends TitleStrategy {
  constructor(private readonly title: Title) {
    super();
  }

  override updateTitle(routerState: any) {
    const title = this.buildTitle(routerState);
    if (title) {
      this.title.setTitle(`${title} - ${siteConfig.name}`);
    } else {
      this.title.setTitle(siteConfig.name);
    }
  }
}

const routes: Routes = [
  {
    path: "",
    children: [
      {
        path: "",
        title: "Home",
        loadComponent: () =>
          import("./features/home/home.component").then((m) => m.HomeComponent),
      },
      {
        path: "radar",
        title: "Radar",
        loadComponent: () =>
          import("./features/tech-radar/tech-radar.component").then(
            (m) => m.TechRadarComponent
          ),
      },
      {
        path: "solutions/new",
        title: "Submit Solution",
        loadChildren: () =>
          import("./features/submit-solution/submit-solution.module").then(
            (m) => m.SubmitSolutionModule
          ),
      },
      {
        path: "solutions",
        title: "Solution Catalog",
        loadComponent: () =>
          import("./features/solution-catalog/solution-catalog.component").then(
            (m) => m.SolutionCatalogComponent
          ),
      },
      {
        path: "solutions/:slug",
        title: "Solution Details",
        loadComponent: () =>
          import("./features/solution-detail/solution-detail.component").then(
            (m) => m.SolutionDetailComponent
          ),
      },
      {
        path: "categories",
        title: "Categories",
        loadChildren: () =>
          import("./features/categories/categories.module").then(
            (m) => m.CategoriesModule
          ),
      },
      {
        path: "about",
        title: "About",
        loadChildren: () =>
          import("./features/about/about.module").then((m) => m.AboutModule),
      },
      {
        path: "manage",
        title: "Manage Content",
        canActivate: [AuthGuard],
        loadChildren: () =>
          import("./features/management/management.module").then(
            (m) => m.ManagementModule
          ),
      },
    ],
  },
  {
    path: "**",
    title: "404 Not Found",
    loadComponent: () =>
      import("./features/not-found/not-found.component").then(
        (m) => m.NotFoundComponent
      ),
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
  providers: [{ provide: TitleStrategy, useClass: CustomTitleStrategy }],
})
export class AppRoutingModule {}
