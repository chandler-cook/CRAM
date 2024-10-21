$(document).ready(function() {
    // Toggle APT dropdown
    $('#btnChooseAPTs').click(function(e) {
        e.preventDefaults();
        $('#aptDropdown').toggle();
        loadAPTs(); // Load APTs from a text file
    });

    // Function to load APTs from a text file
    function loadAPTs() {
        $.get('/static/apts/APT-List.txt', function(data) {
            let aptArray = data.split('\n');
            let aptList = $('#aptList');
            aptList.empty(); // Clear any previous checkboxes

            // Add checkboxes for each APT
            aptArray.forEach(function(apt) {
                if (apt.trim() !== '') {
                    aptList.append(`
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="${apt.trim()}" id="${apt.trim()}">
                            <label class="form-check-label" for="${apt.trim()}">
                                ${apt.trim()}
                            </label>
                        </div>
                    `);
                }
            });
        });
    }

    // Handle submit action for APTs
    $('#btnSubmitAPTs').click(function() {
        let checkedAPTs = [];
        $('#aptList input:checked').each(function() {
            checkedAPTs.push($(this).val());
        });

        // Send checked APTs to the /apts route
        $.ajax({
            url: '/apts',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ "checked_apts": checkedAPTs }),
            success: function(response) {
                alert('Scores updated successfully!');
                // Update the scores on the frontend
                $('.big-number').text(response.overall_score);
                $('.small-number#software').text(response.sw_score);
                $('.small-number#hardware').text(response.hw_score);
                $('.small-number#physical').text(response.phy_score);
            },
            error: function() {
                alert('An error occurred while processing APTs');
            }
        });
    });
});
