$ () =>
    elts = []
    $('.datepicker').datepicker(
        onSelect: (d, inst) =>
            @[inst.id + "Date"] = new Date(d)
            for elt in elts
                if elt.plotable
                    elt.clear()
                    elt.fetch()
        dateFormat: 'yy-mm-dd'
        maxDate: new Date()
    )
    $("#from").datepicker("setDate", '-1m')
    $("#to").datepicker("setDate", new Date())
    @fromDate = $("#from").datepicker("getDate")
    @toDate = $("#to").datepicker("getDate")

    for elt in $(".graph")
        elt = $ elt
        elts.push(new @[elt.attr('data-graph')](elt))


