import { Routes } from '@angular/router';
import { AuthComponent } from './auth/auth.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { LandingComponent } from './landing/landing.component';
import { OverviewComponent } from './dashboard/overview/overview.component';
import { StudentsComponent } from './students/students.component';
import { TeachersComponent } from './teachers/teachers.component';
import { CoursesComponent } from './courses/courses.component';
import { StudentGradesComponent } from './students/student-grades.component';
import { AnalyticsComponent } from './analytics/analytics.component';

export const routes: Routes = [
    { path: '', component: LandingComponent },
    { path: 'auth', component: AuthComponent },
    {
        path: 'dashboard',
        component: DashboardComponent,
        children: [
            { path: '', component: OverviewComponent },
            { path: 'students', component: StudentsComponent },
            { path: 'grades', component: StudentGradesComponent },
            { path: 'teachers', component: TeachersComponent },
            { path: 'courses', component: CoursesComponent },
            { path: 'analytics', component: AnalyticsComponent }
        ]
    }
];

