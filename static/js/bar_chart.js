// Set our margins
var BarChart=function(target,colors){
    target = target || "#chart_div";
    colors = colors || ["#308fef", "#5fa9f3", "#1176db"]
    var margin = {
        top: 20,
        right: 20,
        bottom: 30,
        left: 60
        },
    width = 700 - margin.left - margin.right,
    height = 350 - margin.top - margin.bottom;
    this.x = d3.scale.ordinal().rangeRoundBands([0, width], .1);
    this.y = d3.scale.linear().rangeRound([height, 0]);
    this.color = d3.scale.ordinal().range();
    this.xAxis = d3.svg.axis().scale(this.x).orient("bottom").tickFormat(d3.format(".d"));
    this.yAxis = d3.svg.axis().scale(this.y).orient("left").tickFormat(d3.format(".2s"));
    this.svg =  d3.select(target).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    this.load=function(url){
        this._data = $.getJSON(url)
        this._xdata = Object.keys(this._data).sort();
        this._ydata = [];
        for (key in this._xdata){
            this.y_data.append(new Date(this._xdata[key]*1000))
        }
        this.x.domain(this._xdata)
        this.y.domain(this._ydata)
    }
    return this
}



// Our X scale


// Our Y scale

// Our color bands


// Use our X scale to set a bottom axis


// Same for our left axis
