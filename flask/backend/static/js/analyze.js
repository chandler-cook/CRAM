/* Switches from divUpload to divOverview */
$(document).on('click', '#btnAnalyze', function (e) {
    e.preventDefault();
    const projectName = $('#txtName').val().trim();
    const fileInput = $('#txtFile')[0].files[0];

    if (!projectName || !fileInput) {
        alert("Please provide a project name and upload a file.");
        return;
    }

    let formData = new FormData();
    formData.append('projectName', projectName);
    formData.append('pdf', fileInput);

    // Show the busy-load spinner before making the AJAX request
    $('body').busyLoad("show");

    $.ajax({
        url: '/analyze',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            let content = `<p><strong>Project Name:</strong> ${response.project_name}</p>`;
            $('#resultDisplay').html(content);

            softwareScore = response.sw_score;
            // Update the big circle with the resiliency score
            $('.big-number').text(response.resiliency_score);

            // Update the smaller circles with respective scores
            $('#btnSoftware .small-number').text(response.sw_score);
            $('#btnHardware .small-number').text(response.hw_score);
            $('#btnPhysical .small-number').text(response.physical_score);

            // Hide the busy-load spinner once the request is successful
            $('body').busyLoad("hide");

            $('#divUpload').slideUp(function () {
                $('#divOverview').slideDown();
            });
        },
        error: function (response) {
            // Hide the busy-load spinner even in case of an error
            $('body').busyLoad("hide");
            alert('Error processing file: ' + response.responseJSON.error);
        }
    });
});

$(document).on('click', '#btnReset', function () {
    $('#txtName').val('');
    $('#txtFile').val('');
});
