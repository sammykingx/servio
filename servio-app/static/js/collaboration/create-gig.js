function gigData() {
  return {
    payload: {
      title: '',
      description: '',
      visibility: 'public',
      startDate: null,
      endDate: null,
      projectBudget: 0,

      // roles are injected / bound, not owned
      roles: [],
    },

    // called once after gigRole initializes
    attachRoles(roleStore) {
      this.payload.roles = roleStore.roles;
    },

    syncDatesFromCalendar(calendarInstance) {
      if (!calendarInstance) return;

      this.payload.startDate = calendarInstance.selectedStart
        ? calendarInstance.selectedStart.toISOString().split('T')[0]
        : null;

      this.payload.endDate = calendarInstance.selectedEnd
        ? calendarInstance.selectedEnd.toISOString().split('T')[0]
        : null;
    },

    buildPayload() {
      return {
        title: this.payload.title.trim(),
        description: this.payload.description.trim(),
        visibility: this.payload.visibility,
        startDate: this.payload.startDate,
        endDate: this.payload.endDate,
        projectBudget: Number(this.payload.projectBudget),
        roles: this.payload.roles.map(r => ({
          nicheId: r.nicheId || null,
          professionalId: r.professionalId || null,
          budget: Number(r.budget),
          description: r.description?.trim() || '',
          workload: r.workload,
        })),
      };
      },
    submit() {
      // 1️⃣ pull dates from calendar
      this.syncDatesFromCalendar(
        Alpine.$data(this.$refs.calendar)
      );

      // 2️⃣ build final payload
      const payload = this.buildPayload();

      console.log('SUBMIT PAYLOAD →', payload);

      // 3️⃣ send / save / navigate
      // fetch('/api/gigs', {...})
    },
  };
}
