// Note: This function relies on the jquery i18n plugin.
// The values that need to be provided are:
// seconds.s
// weight.g


function drawChart(data)
{

    console.log("Drawing chart. Number of data items: " + data.length);

    data.forEach(function(d) {
        d.value = +d.value;
        d.number = +d.number;

        console.log(d.value);
    });

    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var area = d3.svg.area()
        .x(function(d) { return x(d.number * 0.03); })
        .y0(height)
        .y1(function(d) { return y(d.value); });

    var line = d3.svg.line()
        .x(function(d) { return x(d.number * 0.03); })
        .y(function(d) { return y(d.value); })
        .interpolate("linear");

    var svg = d3.select("#plotModalBody").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Add a background color.
    d3.select("svg")
        .insert("rect", "g")// Insert rect before g.
        .attr("class", "background")
        .attr("width", "100%")
        .attr("height", "100%");

    var x_domain = d3.extent(data, function(d) { return d.number*0.03; });
    x_domain[1] += 0.3;
    x.domain(x_domain);
    y.domain([0, d3.max(data, function(d) { return d.value; })]);

    svg.append("path")
      .datum(data)
      .attr("class", "area")
      .attr("d", area);

    svg.append("path")
        .datum(data)
        .attr("d", line)
        .attr("class", "gfxline");

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .append("text")
      .attr("x", width-2)
      .attr("dy", -6)
      .style("text-anchor", "end")
      .text($.i18n._("seconds.s"));

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text($.i18n._("weight.g"));


} //! function drawChart