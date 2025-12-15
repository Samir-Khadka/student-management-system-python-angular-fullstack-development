import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
    selector: 'app-analytics',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="content-padding">
        <div class="page-header">
            <div class="page-title">
                <h1>Analytics Dashboard</h1>
                <span class="page-subtitle">Real-time data insights</span>
            </div>
        </div>

        <div class="analytics-grid">
            <!-- Gender Distribution -->
            <div class="content-card">
                <h3>Gender Distribution</h3>
                <div *ngFor="let item of genderData" class="stat-row">
                    <span class="label">{{item.gender}}</span>
                    <div class="bar-container">
                        <div class="bar" [style.width.%]="item.percentage"></div>
                    </div>
                    <span class="value">{{item.count}} ({{item.percentage}}%)</span>
                </div>
            </div>

             <!-- Performance by Support -->
             <div class="content-card">
                <h3>Performance by Parental Support</h3>
                <div *ngFor="let item of supportData" class="stat-row">
                    <span class="label">{{item.parental_support | titlecase}}</span>
                    <div class="bar-container">
                        <div class="bar blue" [style.width.%]="item.average_grade"></div>
                    </div>
                    <span class="value">Avg: {{item.average_grade}}%</span>
                </div>
            </div>

            <!-- Internet Access Impact -->
            <div class="content-card">
                <h3>Internet Access Impact</h3>
                <div *ngFor="let item of internetData" class="stat-row">
                    <span class="label">{{item.has_internet_access ? 'Yes' : 'No'}}</span>
                    <div class="bar-container">
                        <div class="bar green" [style.width.%]="item.average_grade"></div>
                    </div>
                    <span class="value">Avg: {{item.average_grade}}%</span>
                </div>
                <!-- Pass Rate Comparison -->
                 <div *ngFor="let item of internetData" class="stat-row mt-2">
                    <span class="label small">Pass Rate ({{item.has_internet_access ? 'Yes' : 'No'}})</span>
                    <div class="bar-container small">
                         <div class="bar purple" [style.width.%]="item.pass_rate"></div>
                    </div>
                     <span class="value small">{{item.pass_rate}}%</span>
                 </div>
            </div>
        </div>

        <!-- At Risk Students Table -->
        <div class="content-card full-width">
            <div class="card-header-risk">
                <h3>⚠️ At-Risk Students (Below 40%)</h3>
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Grade</th>
                            <th>Absences</th>
                            <th>Risk Factors</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr *ngFor="let student of atRiskData">
                            <td class="font-medium">{{student.name}}</td>
                            <td class="text-red-500 font-bold">{{student.final_grade}}%</td>
                            <td>{{student.absences}}</td>
                            <td>
                                <span class="risk-tag" *ngFor="let localFactor of student.risk_factors">
                                    {{localFactor}}
                                </span>
                            </td>
                        </tr>
                        <tr *ngIf="atRiskData.length === 0">
                            <td colspan="4" class="text-center text-muted">No students currently at risk.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    `,
    styles: [`
        .content-padding { 
            padding: 2rem; 
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.4) 0%, rgba(30, 41, 59, 0.4) 100%);
            min-height: 100vh;
        }
        
        .page-header { 
            margin-bottom: 2.5rem; 
            padding: 2rem;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 139, 250, 0.05) 100%);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 1.5rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.1);
        }
        
        .page-title h1 { 
            font-size: 2.25rem; 
            font-weight: 700; 
            color: white; 
            margin-bottom: 0.5rem; 
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .page-subtitle { 
            color: #c4b5fd; 
            font-size: 1rem;
            font-weight: 500;
        }
        
        .analytics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); 
            gap: 2rem; 
            margin-bottom: 2rem; 
        }
        
        .content-card { 
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(139, 92, 246, 0.15);
            border-radius: 1.5rem; 
            padding: 2rem; 
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2),
                        0 0 0 1px rgba(255, 255, 255, 0.02) inset;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .content-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #8b5cf6, #a78bfa, #8b5cf6);
            background-size: 200% 100%;
            animation: shimmer 3s linear infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .content-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(139, 92, 246, 0.25),
                        0 0 0 1px rgba(139, 92, 246, 0.2) inset;
            border-color: rgba(139, 92, 246, 0.3);
        }
        
        .full-width { 
            grid-column: 1 / -1; 
        }
        
        h3 { 
            color: white; 
            margin-bottom: 2rem; 
            font-size: 1.25rem; 
            font-weight: 600;
            padding-bottom: 1rem;
            border-bottom: 2px solid transparent;
            background: linear-gradient(90deg, rgba(139, 92, 246, 0.3) 0%, transparent 100%);
            border-image: linear-gradient(90deg, #8b5cf6, transparent) 1;
            border-image-slice: 0 0 1 0;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        h3::before {
            content: '';
            width: 4px;
            height: 24px;
            background: linear-gradient(180deg, #8b5cf6, #a78bfa);
            border-radius: 2px;
            box-shadow: 0 0 12px rgba(139, 92, 246, 0.5);
        }
        
        .card-header-risk h3 { 
            color: #fca5a5; 
            background: linear-gradient(90deg, rgba(248, 113, 113, 0.2) 0%, transparent 100%);
            border-image: linear-gradient(90deg, #f87171, transparent) 1;
        }
        
        .card-header-risk h3::before {
            background: linear-gradient(180deg, #f87171, #fca5a5);
            box-shadow: 0 0 12px rgba(248, 113, 113, 0.5);
        }

        .stat-row { 
            display: flex; 
            align-items: center; 
            gap: 1.25rem; 
            margin-bottom: 1.5rem; 
            color: #e2e8f0;
            padding: 0.75rem;
            border-radius: 0.75rem;
            transition: all 0.3s ease;
        }
        
        .stat-row:hover {
            background: rgba(139, 92, 246, 0.05);
            transform: translateX(4px);
        }
        
        .label { 
            min-width: 120px; 
            font-weight: 600; 
            font-size: 0.95rem; 
            color: #f1f5f9;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .label::before {
            content: '';
            width: 8px;
            height: 8px;
            background: linear-gradient(135deg, #8b5cf6, #a78bfa);
            border-radius: 50%;
            box-shadow: 0 0 8px rgba(139, 92, 246, 0.6);
        }
        
        .value { 
            min-width: 120px; 
            text-align: right; 
            font-variant-numeric: tabular-nums; 
            font-weight: 600;
            color: #c4b5fd;
            font-size: 1rem;
        }
        
        .bar-container { 
            flex: 1; 
            height: 12px; 
            background: rgba(255,255,255,0.05); 
            border-radius: 100px; 
            overflow: hidden;
            position: relative;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .bar { 
            height: 100%; 
            background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
            border-radius: 100px; 
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            box-shadow: 0 0 16px rgba(139, 92, 246, 0.6),
                        inset 0 1px 0 rgba(255,255,255,0.3);
        }
        
        .bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 50%;
            background: linear-gradient(180deg, rgba(255,255,255,0.2) 0%, transparent 100%);
            border-radius: 100px 100px 0 0;
        }
        
        .bar.blue { 
            background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
            box-shadow: 0 0 16px rgba(59, 130, 246, 0.6),
                        inset 0 1px 0 rgba(255,255,255,0.3);
        }
        
        .bar.green { 
            background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.6),
                        inset 0 1px 0 rgba(255,255,255,0.3);
        }
        
        .bar.purple { 
            background: linear-gradient(90deg, #a855f7 0%, #c084fc 100%);
            box-shadow: 0 0 16px rgba(168, 85, 247, 0.6),
                        inset 0 1px 0 rgba(255,255,255,0.3);
        }

        .mt-2 { margin-top: 1rem; }
        
        .small { 
            font-size: 0.85rem; 
            color: #cbd5e1; 
            font-weight: 500;
        }
        
        .bar-container.small { 
            height: 8px; 
        }

        /* Table Styles */
        .table-container { 
            overflow-x: auto; 
            border-radius: 0.75rem;
            background: rgba(0,0,0,0.2);
            padding: 0.5rem;
        }
        
        .data-table { 
            width: 100%; 
            border-collapse: separate;
            border-spacing: 0;
            color: #cbd5e1; 
        }
        
        .data-table th { 
            text-align: left; 
            padding: 1.25rem 1rem; 
            background: rgba(139, 92, 246, 0.1);
            color: #f1f5f9; 
            font-weight: 600; 
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid rgba(139, 92, 246, 0.3);
        }
        
        .data-table th:first-child {
            border-radius: 0.5rem 0 0 0;
        }
        
        .data-table th:last-child {
            border-radius: 0 0.5rem 0 0;
        }
        
        .data-table tr {
            transition: all 0.3s ease;
        }
        
        .data-table tbody tr:hover {
            background: rgba(139, 92, 246, 0.05);
            transform: scale(1.01);
        }
        
        .data-table td { 
            padding: 1.25rem 1rem; 
            border-bottom: 1px solid rgba(255,255,255,0.05); 
            font-size: 0.95rem;
        }
        
        .font-medium { 
            font-weight: 600; 
            color: white; 
        }
        
        .text-red-500 { 
            color: #fca5a5; 
            font-weight: 700;
            text-shadow: 0 0 8px rgba(248, 113, 113, 0.3);
        }
        
        .text-center { 
            text-align: center; 
            padding: 3rem !important;
        }
        
        .text-muted { 
            color: #64748b; 
        }

        .risk-tag { 
            display: inline-block; 
            background: linear-gradient(135deg, rgba(248, 113, 113, 0.15) 0%, rgba(252, 165, 165, 0.1) 100%);
            color: #fca5a5; 
            padding: 0.35rem 0.85rem; 
            border-radius: 100px; 
            font-size: 0.75rem; 
            margin-right: 0.5rem; 
            margin-bottom: 0.25rem;
            border: 1px solid rgba(248, 113, 113, 0.3); 
            font-weight: 600;
            letter-spacing: 0.02em;
            box-shadow: 0 2px 8px rgba(248, 113, 113, 0.2);
            transition: all 0.3s ease;
        }
        
        .risk-tag:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(248, 113, 113, 0.3);
            background: linear-gradient(135deg, rgba(248, 113, 113, 0.2) 0%, rgba(252, 165, 165, 0.15) 100%);
        }
    `]
})
export class AnalyticsComponent implements OnInit {
    private apiService = inject(ApiService);
    private cdr = inject(ChangeDetectorRef);

    genderData: any[] = [];
    supportData: any[] = [];
    internetData: any[] = [];
    atRiskData: any[] = [];

    ngOnInit() {
        this.loadData();
    }

    loadData() {
        this.apiService.getGenderDistribution().subscribe({
            next: (res: any) => { this.genderData = res.gender_distribution; this.cdr.detectChanges(); }
        });

        this.apiService.getPerformanceBySupport().subscribe({
            next: (res: any) => { this.supportData = res.performance_by_support; this.cdr.detectChanges(); }
        });

        this.apiService.getInternetAccessImpact().subscribe({
            next: (res: any) => { this.internetData = res.internet_access_impact; this.cdr.detectChanges(); }
        });

        this.apiService.getAtRiskStudents().subscribe({
            next: (res: any) => { this.atRiskData = res.at_risk_students; this.cdr.detectChanges(); }
        });
    }
}
