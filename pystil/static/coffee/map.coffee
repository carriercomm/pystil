class @Map extends @Base
    type: 'map'

    constructor: (@elt) ->
        @data = []
        $("body").append($('<div>')
            .attr('id', 'maptooltip')
            .css(position: 'absolute', display: 'none'))

        $.ajax
            url: "/static/worldmap.svg"
            method: 'GET'
            dataType: 'html'
            async: false #FIXME
            success: (response) => @elt.html response
        @plotable = true
        super

    clear: () ->
        super
        $(".country").css(fill: '').find('title').remove()

    reply: (response) =>
        super
        @data = response
        @plot()
        @make_tooltip()

    plot: () ->
        for country in @data.list
            $("#" + country.key.split("$")[1].toLowerCase())
                .css(fill: 'rgba(0, 0, 255, ' + ((country.count / @data.max) * 0.7 + 0.2) + ')')
                .prepend($('<title>').text(country.key.split("$")[0].toLowerCase() + ": " + country.count))

    make_tooltip: () ->
        $(".country").mouseover (e) ->
            $('#maptooltip').css(top: e.pageY + 10 + 'px', left: e.pageX + 10 + 'px', display: 'block'
            ).text($('title', e.currentTarget).text())
        $(".country").mouseout (e) -> $('#maptooltip').css(display: 'none')
