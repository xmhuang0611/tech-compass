import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Subscription } from 'rxjs';

// External libraries
declare const d3: any;
declare const radar_visualization: any;

// Data interface definition
interface TechRadarEntry {
  quadrant: number;  // Index of quadrant (0-3)
  ring: number;      // Index of ring (0-3)
  label: string;     // Technology name
  active: boolean;   // Active status
  moved: number;     // Movement status
}

interface TechRadarData {
  date: string;      // Radar chart date
  entries: TechRadarEntry[];  // Technology item list
}

@Component({
  selector: 'tc-tech-radar',
  standalone: true,
  imports: [
    CommonModule,
    BreadcrumbModule
  ],
  templateUrl: './tech-radar.component.html',
  styleUrls: ['./tech-radar.component.scss']
})
export class TechRadarComponent implements OnInit, OnDestroy {
  // Constant definition
  private readonly MAX_QUADRANTS = 4;  // Maximum number of quadrants
  private readonly MAX_RINGS = 4;      // Maximum number of rings
  private readonly SCRIPT_LOAD_DELAY = 100;  // Script load delay (milliseconds)

  // Component state
  private dataSubscription: Subscription | null = null;
  private scriptsLoaded = false;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.initializeRadar();
  }

  ngOnDestroy() {
    this.cleanup();
  }

  /**
   * Initialize radar visualization:
   * 1. Load required scripts
   * 2. Fetch and display data
   */
  private initializeRadar(): void {
    this.loadScripts()
      .then(() => this.loadTechRadarData())
      .catch(error => console.error('Failed to initialize radar:', error));
  }

  /**
   * Load required JavaScript files
   */
  private loadScripts(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.scriptsLoaded) {
        resolve();
        return;
      }

      const d3Script = this.createScript('assets/js/d3.v4.min.js');
      const radarScript = this.createScript('assets/js/radar.js');

      d3Script.onerror = error => reject(error);
      radarScript.onerror = error => reject(error);

      // Load scripts sequentially
      d3Script.onload = () => document.body.appendChild(radarScript);
      radarScript.onload = () => {
        this.scriptsLoaded = true;
        setTimeout(() => resolve(), this.SCRIPT_LOAD_DELAY);
      };

      document.body.appendChild(d3Script);
    });
  }

  /**
   * Create script element
   * @param src Script source path
   * @returns HTMLScriptElement
   */
  private createScript(src: string): HTMLScriptElement {
    const script = document.createElement('script');
    script.src = src;
    script.type = 'text/javascript';
    return script;
  }

  /**
   * Load technology radar data
   */
  private loadTechRadarData(): void {
    if (!this.scriptsLoaded || typeof radar_visualization === 'undefined') {
      console.error('Required scripts are not loaded');
      return;
    }

    this.dataSubscription = this.http.get<TechRadarData>(`${environment.apiUrl}/tech-radar/data`)
      .subscribe({
        next: (data) => {
          if (this.isValidData(data)) {
            const validEntries = this.processEntries(data.entries);
            this.visualizeRadar({ date: data.date, entries: validEntries });
          }
        },
        error: (error) => console.error('Error loading tech radar data:', error)
      });
  }

  /**
   * Verify data format is valid
   * @param data Radar chart data
   * @returns boolean
   */
  private isValidData(data: any): data is TechRadarData {
    if (!data || !data.entries || !Array.isArray(data.entries)) {
      console.error('Invalid data format:', data);
      return false;
    }
    return true;
  }

  /**
   * Process and verify data items
   * @param entries Original item data
   * @returns TechRadarEntry[]
   */
  private processEntries(entries: TechRadarEntry[]): TechRadarEntry[] {
    return entries
      .map(entry => this.validateAndCleanEntry(entry))
      .filter((entry): entry is TechRadarEntry => entry !== null);
  }

  /**
   * Verify and clean single item data
   * @param entry Original item
   * @returns TechRadarEntry | null
   */
  private validateAndCleanEntry(entry: TechRadarEntry): TechRadarEntry | null {
    const quadrant = Number(entry.quadrant);
    const ring = Number(entry.ring);
    
    if (quadrant >= this.MAX_QUADRANTS || ring >= this.MAX_RINGS) {
      console.warn(`Invalid entry skipped: ${entry.label} (quadrant: ${quadrant}, ring: ${ring})`);
      return null;
    }

    return {
      quadrant,
      ring,
      label: String(entry.label),
      active: Boolean(entry.active),
      moved: Number(entry.moved)
    };
  }

  /**
   * Visualize radar chart
   * @param data Processed radar chart data
   */
  private visualizeRadar(data: TechRadarData): void {
    const svgElement = document.getElementById('radar');
    if (!svgElement) {
      console.error('SVG element not found');
      return;
    }

    try {
      svgElement.innerHTML = '';
      radar_visualization(this.createRadarConfig(data));
    } catch (error) {
      console.error('Error initializing radar visualization:', error);
    }
  }

  /**
   * Create radar chart configuration
   * @param data Radar chart data
   * @returns Radar chart configuration object
   */
  private createRadarConfig(data: TechRadarData): any {
    return {
      svg_id: "radar",
      width: 500,
      height: 500,
      colors: {
        background: '#fff',
        grid: '#dddde0',
        inactive: '#ddd'
      },
      title: "Technology Radar",
      date: data.date,
      quadrants: [
        { name: "Languages" },
        { name: "Infrastructure" },
        { name: "Datastores" },
        { name: "Data Management" }
      ],
      rings: [
        { name: "ADOPT", color: "#5ba300" },
        { name: "TRIAL", color: "#009eb0" },
        { name: "ASSESS", color: "#c7ba00" },
        { name: "HOLD", color: "#e09b96" }
      ],
      entries: data.entries,
      // Layout configuration
      radiality: 0.8,
      rotation: Math.PI / 2,
      print_layout: true,
      radius: 400,
      radial_min: 20,
      radial_max: 400,
      // Segment configuration
      segment: {
        radial_padding: 30,
        width: Math.PI / 2
      },
      quadrant_width: Math.PI / 2,
      quadrant_radial_padding: 30,
      // Ring configuration
      ring_margin: 30,
      ring_width: 95,
      ring_radius_margin: 30,
      ring_radius_width: 95,
      ring_label_height: 14,
      ring_label_font_size: 12,
      ring_label_padding: 10
    };
  }

  /**
   * Clean component resources
   */
  private cleanup(): void {
    if (this.dataSubscription) {
      this.dataSubscription.unsubscribe();
    }
    this.removeScripts();
  }

  /**
   * Remove loaded scripts
   */
  private removeScripts(): void {
    if (this.scriptsLoaded) {
      const scripts = document.querySelectorAll('script[src*="d3.v4.min.js"], script[src*="radar.js"]');
      scripts.forEach(script => script.remove());
      this.scriptsLoaded = false;
    }
  }
}