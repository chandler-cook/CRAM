$(document).on('click', '#btnSoftware', function () {
    $('#divOverview').slideUp(function () {
        $('#divSoftware').slideDown();
        // Update the big circle in #divSoftware with the software score
        $('#divSoftware .big-number').text(softwareScore);  // Update the big circle
    });

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
                </div>
            `;

            // Loop through each endpoint group and create an accordion for each
            Object.keys(groupedData).forEach((endpoint, endpointIndex) => {
                let cveListItems = '';  // Store the CVE list for each endpoint

                // Create clickable CVE items for this endpoint
                groupedData[endpoint].forEach((cve, cveIndex) => {
                    cveListItems += `
                        <li class="list-group-item cve-item" data-cve-id="${cve.cve_id}" data-index="${endpointIndex}-${cveIndex}">
                            ${cve.cve_id} (Score: ${cve.cvss_base_score})
                        </li>
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
                                <ul class="list-group" id="cveList-${endpointIndex}">
                                    ${cveListItems}
                                </ul>
                                <div id="cveDetail-${endpointIndex}" class="cve-detail mt-3" style="display: none;">
                                    <!-- CVE details will appear here -->
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

            // Add event listener for "Back to Overview" button
            $('#btnBackToOverview').on('click', function () {
                $('#divSoftware').slideUp();  // Hide the software section
                $('#divOverview').slideDown();  // Show the overview section
            });

            // Event listener for clicking on a CVE item
            $('.cve-item').on('click', function () {
                const cveId = $(this).data('cve-id');
                const index = $(this).data('index').split('-');
                const endpointIndex = index[0];
                const cveIndex = index[1];
                
                // Find the CVE details and display them
                const cve = groupedData[Object.keys(groupedData)[endpointIndex]][cveIndex];
                const cveDetailDiv = $(`#cveDetail-${endpointIndex}`);

                const cveDetailContent = `
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
                `;

                // Update the details section and show it
                cveDetailDiv.html(cveDetailContent).slideDown();
                
                // Event listener for "Resolve" button
                $('.btnResolve').on('click', function () {
                    const scoreToAdd = parseFloat($(this).data('score'));
                    const cveId = $(this).data('cve-id');
                    
                    // Remove the resolved CVE
                    $(`#cve-${cveId}`).remove();
                    softwareScore += scoreToAdd;
                    
                    // Update the displayed software score
                    $('#divSoftware .big-number').text(softwareScore.toFixed(1));
                    
                    // Hide the details after resolving
                    cveDetailDiv.slideUp();
                });
            });

        } else {
            alert('No CVE data available');
        }
    }).fail(function () {
        alert('Failed to load CVE data');
    });
});
