$(document).ready(function () {
    // Connect to the Socket.IO server.
    // The connection URL has the following format, relative to the current page:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io();

    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('status', function (res) {
        $('#status').append(`<span class="${res.class}">${res.message}</span>`)
        $('button#stop').prop('disabled', true)
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
        $(`#body-${res.section_id}`).append(`<p class="${res.class} m-0">${res.message}</p>`)
        filter('success')
        filter('warning')
        filter('danger')
    })

    // stop background task execution
    $("button#stop").on('click', function () {
        socket.emit('stop')
    })

    $("a#go-back").on('click', function () {
        socket.emit('stop')
    })

    $(window).on('beforeunload', function (event) {
        socket.emit('stop')
    })

    // back to top
    $(window).on('scroll', function () {
        if ($(this).scrollTop() > 50) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });

    $('#back-to-top').on('click', function () {
        $('body,html').animate({
            scrollTop: 0
        }, 400);
        return false;
    });

    // filter messages
    function filter(type) {
        const messages = document.querySelectorAll(`p.text-${type}`)
        const checkbox = document.querySelector(`#${type}-checkbox`)
        for (let message of messages) {
            if (checkbox.checked) {
                message.style.display = 'block'
            } else {
                message.style.display = 'none'
            }
        }
    }
    $('#success-checkbox').on('change', function () {
        filter("success");
    })
    $('#warning-checkbox').on('change', function () {
        filter('warning');
    })
    $('#danger-checkbox').on('change', function () {
        filter('danger');
    })
});