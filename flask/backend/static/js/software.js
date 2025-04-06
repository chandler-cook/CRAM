$(document).on('click', '#btnSoftware', function () {
    
    $.getJSON('/software', function (data) {
        let groupedData = {};  // To group CVEs by endpoint_name

        // Ensure the data contains the 'cves' array
        if (data.cves && Array.isArray(data.cves)) {
            // Group CVEs by endpoint_name
            data.cves.forEach(cve => {
                const endpoint = cve.endpoint_name || 'No Endpoint';  // Default group for CVEs without an endpoint name
                if (!groupedData[endpoint]) {
                    groupedData[endpoint] = [];
                }
                groupedData[endpoint].push(cve);
            });

            let accordionContent = '';  // To store all accordion sections

            // Add the "Back to Overview" button at the top
            accordionContent += `
                <div class="d-flex justify-content-end mb-3 sticky-back-button">
                    <button id="btnBackToOverview" class="btn btn-secondary">Back to Overview</button>
                    <button id="btnChangeCriticality" class="btn btn-warning">Change Criticality</button>
                </div>
            `;

            // Loop through each endpoint group and create an accordion for each
            Object.keys(groupedData).forEach((endpoint, endpointIndex) => {
                let cveAccordionItems = '';  // Store the CVE accordion for each endpoint

                // Create clickable accordion items for this endpoint
                groupedData[endpoint].forEach((cve, cveIndex) => {
                    cveAccordionItems += `
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="headingCve${endpointIndex}-${cveIndex}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseCve${endpointIndex}-${cveIndex}" aria-expanded="false" aria-controls="collapseCve${endpointIndex}-${cveIndex}">
                                    ${cve.cve_id} (Score: ${cve.cvss_base_score})
                                </button>
                            </h2>
                            <div id="collapseCve${endpointIndex}-${cveIndex}" class="accordion-collapse collapse" aria-labelledby="headingCve${endpointIndex}-${cveIndex}">
                                <div class="accordion-body">
                                    <h5>CVE Details for ${cve.cve_id}</h5>
                                    <p><strong>Severity:</strong> ${cve.cvss_severity}</p>
                                    <p><strong>Score:</strong> ${cve.cvss_base_score} (${cve.cvss_version})</p>
                                    <p><strong>EPSS Score:</strong> ${cve.epss}</p>
                                    <p><strong>Endpoint Criticality:</strong> ${cve.criticality}</p>
                                    <p><strong>Description:</strong> ${cve.description}</p>
                                    <p><strong>Availability Impact:</strong> ${cve.cvss_vector_description['Availability Impact'] || 'N/A'}</p>
                                    <p><strong>References:</strong></p>
                                    <ul>
                                        ${cve.references ? cve.references.map(ref => `<li><a href="${ref.url}" target="_blank" class="text-info">${ref.url}</a></li>`).join('') : ''}
                                    </ul>
                                    <button class="btn btn-success btnResolve" data-score="${cve.cvss_base_score}" data-cve-id="${cve.cve_id}">Resolve</button>
                                </div>
                            </div>
                        </div>
                    `;
                });

                // Create a new accordion for this endpoint
                accordionContent += `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="heading${endpointIndex}">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${endpointIndex}" aria-expanded="false" aria-controls="collapse${endpointIndex}">
                                ${endpoint}
                            </button>
                        </h2>
                        <div id="collapse${endpointIndex}" class="accordion-collapse collapse" aria-labelledby="heading${endpointIndex}" data-bs-parent="#accordionEndpoints">
                            <div class="accordion-body">
                                <div class="accordion" id="accordionCves${endpointIndex}">
                                    ${cveAccordionItems}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            // Inject the generated accordions into the #divSoftware element
            $('#divSoftware').html(`
                <div class="accordion" id="accordionEndpoints">
                    ${accordionContent}
                </div>
            `);

            $('#divOverview').slideUp(function () {
                $('#divSoftware').slideDown(function () {
                    // Update the big circle in #divSoftware with the software score
                    $('#divSoftware .big-number').text(softwareScore);
                });
            });

            // Use event delegation to listen for clicks on the dynamically generated "Back to Overview" button
            $(document).on('click', '#btnBackToOverview', function () {
                $('#divSoftware').slideUp();  // Hide the software section
                $('#divOverview').slideDown();  // Show the overview section

                $('#btnSoftware .small-number').text(updatedSoftwareScore.toFixed(1));  // Update the software score
                $('#btnHardware .small-number').text(hardwareScore.toFixed(1));  // Keep the existing hardware score
                $('#btnPhysical .small-number').text(physicalScore.toFixed(1));  // Keep the existing physical score
            });

            // Event listener for "Change Criticality" button
            $(document).on('click', '#btnChangeCriticality', function () {
                // Send the AJAX request to trigger the backend process
                $.ajax({
                    url: '/change_criticality',  // Backend route to trigger your changeCrit function
                    type: 'POST',
                    contentType: 'application/json',
                    success: function(response) {
                        const updatedSoftwareScore = response.software_score;
                        // Retrieve existing scores for hardware and physical from the small circles
                        const hardwareScore = parseFloat($('.small-number', '#btnHardware').text()) || 0;  
                        const physicalScore = parseFloat($('.small-number', '#btnPhysical').text()) || 0;
                        // Calculate the new overall score (you can adjust the formula as needed)
                        const overallScore = (updatedSoftwareScore + hardwareScore + physicalScore) / 3;
                        ('#btnSoftware .small-number').text(updatedSoftwareScore.toFixed(1));
                        $('#divOverview .big-number').text(overallScore.toFixed(2));
                        // Now retrieve the updated CVE data and rebuild the accordion
                        $.getJSON('/software', function (data) {
                            // Ensure the data contains the 'cves' array
                            if (data.cves && Array.isArray(data.cves)) {
                                let groupedData = {};  // To group CVEs by endpoint_name

                                // Group CVEs by endpoint_name
                                data.cves.forEach(cve => {
                                    const endpoint = cve.endpoint_name || 'No Endpoint';  // Default group for CVEs without an endpoint name
                                    if (!groupedData[endpoint]) {
                                        groupedData[endpoint] = [];
                                    }
                                    groupedData[endpoint].push(cve);
                                });

                                let accordionContent = '';  // To store all accordion sections

                                // Add the "Back to Overview" and "Change Criticality" buttons at the top
                                accordionContent += `
                                    <div class="d-flex justify-content-between mb-3">
                                        <button id="btnBackToOverview" class="btn btn-secondary">Back to Overview</button>
                                        <button id="btnChangeCriticality" class="btn btn-warning">Change Criticality</button>
                                    </div>
                                `;

                                // Loop through each endpoint group and create an accordion for each
                                Object.keys(groupedData).forEach((endpoint, endpointIndex) => {
                                    let cveAccordionItems = '';  // Store the CVE accordion for each endpoint

                                    // Create clickable accordion items for this endpoint
                                    groupedData[endpoint].forEach((cve, cveIndex) => {
                                        cveAccordionItems += `
                                            <div class="accordion-item">
                                                <h2 class="accordion-header" id="headingCve${endpointIndex}-${cveIndex}">
                                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseCve${endpointIndex}-${cveIndex}" aria-expanded="false" aria-controls="collapseCve${endpointIndex}-${cveIndex}">
                                                        ${cve.cve_id} (Score: ${cve.cvss_base_score})
                                                    </button>
                                                </h2>
                                                <div id="collapseCve${endpointIndex}-${cveIndex}" class="accordion-collapse collapse" aria-labelledby="headingCve${endpointIndex}-${cveIndex}">
                                                    <div class="accordion-body">
                                                        <h5>CVE Details for ${cve.cve_id}</h5>
                                                        <p><strong>Severity:</strong> ${cve.cvss_severity}</p>
                                                        <p><strong>Score:</strong> ${cve.cvss_base_score} (${cve.cvss_version})</p>
                                                        <p><strong>EPSS Score:</strong> ${cve.epss}</p>
                                                        <p><strong>Endpoint Criticality:</strong> ${cve.criticality}</p>
                                                        <p><strong>Description:</strong> ${cve.description}</p>
                                                        <button class="btn btn-success btnResolve" data-score="${cve.cvss_base_score}" data-cve-id="${cve.cve_id}">Resolve</button>
                                                    </div>
                                                </div>
                                            </div>
                                        `;
                                    });

                                    // Create a new accordion for this endpoint
                                    accordionContent += `
                                        <div class="accordion-item">
                                            <h2 class="accordion-header" id="heading${endpointIndex}">
                                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${endpointIndex}" aria-expanded="false" aria-controls="collapse${endpointIndex}">
                                                    ${endpoint}
                                                </button>
                                            </h2>
                                            <div id="collapse${endpointIndex}" class="accordion-collapse collapse" aria-labelledby="heading${endpointIndex}" data-bs-parent="#accordionEndpoints">
                                                <div class="accordion-body">
                                                    <div class="accordion" id="accordionCves${endpointIndex}">
                                                        ${cveAccordionItems}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                });

                                // Inject the generated accordions into the #divSoftware element
                                $('#divSoftware').html(`
                                    <div class="accordion" id="accordionEndpoints">
                                        ${accordionContent}
                                    </div>
                                `);

                                $('#divOverview').slideUp(function () {
                                    $('#divSoftware').slideDown(function () {
                                        // Update the big circle in #divSoftware with the software score
                                        $('#divSoftware .big-number').text(data.software_score);
                                    });
                                });

                            } else {
                                alert('No CVE data available');
                            }
                        });
                    },
                    error: function(err) {
                        console.error('Error changing criticality:', err);
                    }
                });
            });


            // Event listener for "Resolve" button
            $(document).on('click', '.btnResolve', function () {
                const cveId = $(this).data('cve-id');  // Get the CVE ID from the button
                let cveIds = [cveId];  // Replace this with your actual array of CVE IDs to resolve
            
                // Send the resolved CVE IDs to the /software route to remove them from the file
                $.ajax({
                    url: '/software',  // POST request to the /software route
                    type: 'POST',
                    data: JSON.stringify({ cve_ids: cveIds }),  // Send multiple CVE IDs
                    contentType: 'application/json',
                    success: function(response) {
                        console.log('CVEs removed from the file:', response);
                        const updatedSoftwareScore = response.software_score;
                        $('#btnSoftware .small-number').text(updatedSoftwareScore.toFixed(1));
                        $('#softwareScore').text(updatedSoftwareScore.toFixed(1));
                    
                        // Retrieve existing scores for hardware and physical from the small circles
                        const hardwareScore = parseFloat($('.small-number', '#btnHardware').text()) || 0;  
                        const physicalScore = parseFloat($('.small-number', '#btnPhysical').text()) || 0;  

                        // Calculate the new overall score (you can adjust the formula as needed)
                        const overallScore = (updatedSoftwareScore + hardwareScore + physicalScore) / 3;

                        $('#divOverview .big-number').text(overallScore.toFixed(2));
                        $.getJSON('/software', function (data) {
                            // Regenerate the accordion content with the updated CVE data
                            let groupedData = {};
                            if (data.cves && Array.isArray(data.cves)) {
                                data.cves.forEach(cve => {
                                    const endpoint = cve.endpoint_name || 'No Endpoint';
                                    if (!groupedData[endpoint]) {
                                        groupedData[endpoint] = [];
                                    }
                                    groupedData[endpoint].push(cve);
                                });

                                let accordionContent = '';  // Same logic to rebuild accordion

                                // Add the "Back to Overview" button at the top
                                accordionContent += `
                                    <div class="d-flex justify-content-end mb-3 sticky-back-button">
                                        <button id="btnBackToOverview" class="btn btn-secondary">Back to Overview</button>
                                        
                                    </div>
                                `;

                                // Loop through each endpoint group and create an accordion for each
                                Object.keys(groupedData).forEach((endpoint, endpointIndex) => {
                                    let cveAccordionItems = '';  // Store the CVE accordion for each endpoint

                                    // Create clickable accordion items for this endpoint
                                    groupedData[endpoint].forEach((cve, cveIndex) => {
                                        cveAccordionItems += `
                                            <div class="accordion-item">
                                                <h2 class="accordion-header" id="headingCve${endpointIndex}-${cveIndex}">
                                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseCve${endpointIndex}-${cveIndex}" aria-expanded="false" aria-controls="collapseCve${endpointIndex}-${cveIndex}">
                                                        ${cve.cve_id} (Score: ${cve.cvss_base_score})
                                                    </button>
                                                </h2>
                                                <div id="collapseCve${endpointIndex}-${cveIndex}" class="accordion-collapse collapse" aria-labelledby="headingCve${endpointIndex}-${cveIndex}">
                                                    <div class="accordion-body">
                                                        <h5>CVE Details for ${cve.cve_id}</h5>
                                                        <p><strong>Severity:</strong> ${cve.cvss_severity}</p>
                                                        <p><strong>Score:</strong> ${cve.cvss_base_score} (${cve.cvss_version})</p>
                                                        <p><strong>EPSS Score:</strong> ${cve.epss}</p>
                                                        <p><strong>Endpoint Criticality:</strong> ${cve.criticality}</p>
                                                        <p><strong>Description:</strong> ${cve.description}</p>
                                                        <button class="btn btn-success btnResolve" data-score="${cve.cvss_base_score}" data-cve-id="${cve.cve_id}">Resolve</button>
                                                    </div>
                                                </div>
                                            </div>
                                        `;
                                    });

                                    // Create a new accordion for this endpoint
                                    accordionContent += `
                                        <div class="accordion-item">
                                            <h2 class="accordion-header" id="heading${endpointIndex}">
                                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${endpointIndex}" aria-expanded="false" aria-controls="collapse${endpointIndex}">
                                                    ${endpoint}
                                                </button>
                                            </h2>
                                            <div id="collapse${endpointIndex}" class="accordion-collapse collapse" aria-labelledby="heading${endpointIndex}" data-bs-parent="#accordionEndpoints">
                                                <div class="accordion-body">
                                                    <div class="accordion" id="accordionCves${endpointIndex}">
                                                        ${cveAccordionItems}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                });

                                // Inject the generated accordions into the #divSoftware element
                                $('#divSoftware').html(`
                                    <div class="accordion" id="accordionEndpoints">
                                        ${accordionContent}
                                    </div>
                                `);
                            }
                        });
                    },
                    error: function(err) {
                        console.error('Error removing CVEs from the file:', err);
                    }
                });
                
                // Remove the resolved CVE accordion item
                $(this).closest('.accordion-item').remove();
            });
        } else {
            alert('No CVE data available');
        }
    }).fail(function () {
        alert('Failed to load CVE data');
    });
});
