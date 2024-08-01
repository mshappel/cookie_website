document.addEventListener("DOMContentLoaded", () => {
    const daysOfWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

    daysOfWeek.forEach(day => {
        const dayOpenCheckbox = document.getElementById(`id_${day}_open`);
        const dayOpenTimeInput = document.getElementById(`${day}_open_time`);
        const dayCloseTimeInput = document.getElementById(`${day}_close_time`);
        const dayOpenTimeGroup = dayOpenTimeInput ? dayOpenTimeInput.closest('.input-group') : null;
        const dayCloseTimeGroup = dayCloseTimeInput ? dayCloseTimeInput.closest('.input-group') : null;
        const dayOpenTimeLabel = document.querySelector(`label[for="${day}_open_time"]`);
        const dayCloseTimeLabel = document.querySelector(`label[for="${day}_close_time"]`);

        let dayGoldenTicketCheckbox = null;
        let dayGoldenTicketContainer = null;

        if (day === 'saturday' || day === 'sunday') {
            dayGoldenTicketCheckbox = document.getElementById(`id_${day}_golden_ticket`);
            if (dayGoldenTicketCheckbox) {
                dayGoldenTicketContainer = dayGoldenTicketCheckbox.closest('.mb-3');
            }
        }

        function toggleTimeInputs() {
            const isChecked = dayOpenCheckbox.checked;
            const displayStyle = isChecked ? '' : 'none';

            if (dayOpenTimeGroup) dayOpenTimeGroup.style.display = displayStyle;
            if (dayCloseTimeGroup) dayCloseTimeGroup.style.display = displayStyle;
            if (dayOpenTimeLabel) dayOpenTimeLabel.style.display = displayStyle;
            if (dayCloseTimeLabel) dayCloseTimeLabel.style.display = displayStyle;

            if (dayGoldenTicketContainer) dayGoldenTicketContainer.style.display = displayStyle;
        }

        // Initial toggle based on the current state of the checkbox
        toggleTimeInputs();

        // Add event listener to the checkbox
        dayOpenCheckbox.addEventListener('change', toggleTimeInputs);
    });
});