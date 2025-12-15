import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing.component.html',
  styleUrls: [] // Global styles
})
export class LandingComponent {
  private router = inject(Router);

  navigateToAuth() {
    this.router.navigate(['/auth']);
  }
}
