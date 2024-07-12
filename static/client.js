$(document).ready(function () {
    // Connect to the Socket.IO server.
    // The connection URL has the following format, relative to the current page:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io();

    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('response', function (res) {
        $('#log').append(`<p class="${res.class}">${res.message}</p>`)
    });

    socket.on('create_section', function (res) {
        $('#log').append(`
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading-${res.id}">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${res.id}" aria-expanded="true" aria-controls="collapse-${res.id}">
                        ${res.heading}
                    </button>
                </h2>
                <div id="collapse-${res.id}" class="accordion-collapse collapse show" aria-labelledby="heading-${res.id}">
                    <div class="accordion-body" id="body-${res.id}">
                    </div>
                </div>
            </div>
        `)
    })

    socket.on('create_link', function (res) {
        $(`#body-${res.section_id}`).append(`<p class="${res.class}">${res.message}</p>`)
    })

    // stop background task execution
    $("button#stop").on('click', function () {
        socket.emit('stop')
    })
});