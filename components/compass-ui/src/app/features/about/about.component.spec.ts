/// <reference types="jasmine" />

import { ComponentFixture, TestBed } from "@angular/core/testing";
import { AboutComponent } from "./about.component";
import { siteConfig } from "../../core/config/site.config";

describe("AboutComponent", () => {
  let component: AboutComponent;
  let fixture: ComponentFixture<AboutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AboutComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AboutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should load about configuration from siteConfig", () => {
    expect(component.aboutConfig).toBeDefined();
    expect(component.aboutConfig).toEqual(siteConfig.about);
  });

  it("should have hero section with title and subtitle", () => {
    expect(component.aboutConfig.hero).toBeDefined();
    expect(component.aboutConfig.hero.title).toBeDefined();
    expect(component.aboutConfig.hero.subtitle).toBeDefined();
  });

  it("should have team section with members", () => {
    expect(component.aboutConfig.team).toBeDefined();
    expect(component.aboutConfig.team.members).toBeDefined();
    expect(Array.isArray(component.aboutConfig.team.members)).toBeTruthy();
  });
});
