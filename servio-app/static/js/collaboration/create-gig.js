// function gigData() {
//     return {
//         payload: {
//             title: '',
//             description: '',
//             projectBudget: 5000,
//             visibility: 'public',
//             roles: [],        // sync roles here
//             startDate: null,  // sync calendar start
//             endDate: null     // sync calendar end
//         },

//         attachRoles(rolesComponent) {
//             // Watch for role changes and update payload
//             this.payload.roles = rolesComponent.roles;

//             // Use Alpine's reactive watcher
//             this.$watch(
//                 () => rolesComponent.roles,
//                 (newRoles) => {
//                     this.payload.roles = newRoles;
//                 },
//                 { deep: true }
//             );
//         },

//         updateDates(calendar) {
//             this.$watch(
//                 () => calendar.selectedStart,
//                 (start) => {
//                     this.payload.startDate = start ? start.toISOString().split('T')[0] : null;
//                 }
//             );

//             this.$watch(
//                 () => calendar.selectedEnd,
//                 (end) => {
//                     this.payload.endDate = end ? end.toISOString().split('T')[0] : null;
//                 }
//             );
//         },

//         submit() {
//             console.log('Submitting payload:', this.payload);
//             // Add validations
//             if (!this.payload.title) return alert('Title is required');
//             if (!this.payload.startDate || !this.payload.endDate) return alert('Start and End dates are required');
//             if (this.payload.roles.length === 0) return alert('Add at least one role');

//             // Send payload to API
//         }
//     }
// }

function gigData() {
    return {
        payload: {
            title: '',
            description: '',
            projectBudget: 5000,
            visibility: 'public',
            roles: [],  
            startDate: null,
            endDate: null,
        },
    }
}


