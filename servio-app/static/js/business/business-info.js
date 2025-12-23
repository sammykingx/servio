let COUNTRIES = [];

document.addEventListener("DOMContentLoaded", async () => {
	const selections = document.querySelectorAll(".countrySelect");
	const countries = await fetch("/static/js/country-list.json").then(res => res.json());

    COUNTRIES = countries;

	if (!selections.length) return;
	
	selections.forEach(selection => {
		countries.forEach(country => {
			const option = document.createElement("option");
			option.value = country.name;
			option.textContent = country.name;
			option.className = "text-gray-700 dark:bg-gray-900 dark:text-gray-400";
		
		    selection.appendChild(option);
	    });
	})	
});
