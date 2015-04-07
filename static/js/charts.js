function charts(div1,div2) {
    var $charts = this
    $charts.load_url=function(url){
        //$.getJSON(url,$charts.on_data)
        $charts.make_charts()
    };
    $charts.on_data2=function(data){
        console.log("OK")
        console.log(data);
        data["bindto"]=div2
        $charts.c3 = c3.generate(data)
    }
    $charts.on_data = function(data){
           setTimeout(function(){
            var x = Object.keys(data).sort()
            var date1 = new Date(parseInt(x[0])*1000)
            var date2 = new Date(parseInt(x[x.length-1])*1000)
            var url="/api/chartData?start="+date1.toISOString()+"&stop="+date2.toISOString();

            console.log("REQUEST:"+url);
            $.getJSON(url,$charts.on_data2)
        },5)
        return data;

    };
    $charts.make_charts = function() {
        $charts.cal = new CalHeatMap();
        var dt = new Date()
        dt.setMonth(dt.getMonth() - 2)
        cal.init({
            itemSelector: div1,
            domain: "month",
            subDomain: "x_day",
            cellSize: 20,
            subDomainTextFormat: "%d",
            start: dt,
            range: 3,
            displayLegend: false,
            data:"/api/calendarData?start={{d:start}}&stop={{d:end}}",
            afterLoadData:$charts.on_data
        })


//        var chart = c3.generate({
//            bindto: div2,
//            data:{
//
//                mimeType:"json",
//                url:"http://localhost:5000/api/chartData?start={{ '{{' }}d:start{{ '}}' }}&stop={{ '{{' }}d:end{{ '}}' }}",
//                type:"bar"
//            },
//            axis: {
//                x: {
//                    type: 'category' // this needed to load string x value
//                }
//            }
//        });
    };
    return this;
}
function init_chart_load(ident1,ident2,url){
    if (!url) url="http://localhost:5000/api/hours?start={{ '{{' }}d:start{{ '}}' }}&stop={{ '{{' }}d:end{{ '}}' }}";
    var c = charts(ident1,ident2)
    c.load_url(url)
}
