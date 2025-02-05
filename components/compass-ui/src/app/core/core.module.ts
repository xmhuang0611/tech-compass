import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { HTTP_INTERCEPTORS } from "@angular/common/http";
import { MenubarModule } from "primeng/menubar";
import { ButtonModule } from "primeng/button";
import { MenuModule } from "primeng/menu";
import { DynamicDialogModule } from "primeng/dynamicdialog";
import { MarkdownModule } from "ngx-markdown";

import { LayoutComponent } from "./layout/layout.component";
import { AuthInterceptor } from "./interceptors/auth.interceptor";

@NgModule({
  declarations: [LayoutComponent],
  imports: [
    CommonModule,
    RouterModule,
    MenubarModule,
    ButtonModule,
    MenuModule,
    DynamicDialogModule,
    MarkdownModule,
  ],
  exports: [LayoutComponent],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    },
  ],
})
export class CoreModule {}
