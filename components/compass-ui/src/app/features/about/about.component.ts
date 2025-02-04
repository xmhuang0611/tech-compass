import { Component } from '@angular/core';
import { siteConfig } from '../../core/config/site.config';

@Component({
  selector: 'tc-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})
export class AboutComponent {
  aboutConfig = siteConfig.about;
  window = window;
}