from pyecharts.charts import Kline,Scatter,Line,Grid,Bar,EffectScatter
from pyecharts import options as opts
from pyecharts.render import make_snapshot
#from pyecharts.globals import SymbolType,ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.globals import CurrentConfig, NotebookType
CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB
from snapshot_pyppeteer import snapshot
from pyecharts.render import make_snapshot

class KChartData:
    def __init__(self,name,df,freq='D',precision=2):
        '''
        @params:
        - name: str                      #图例名称
        - df:  pandas.DataFrame          #columns包含 [u'open', u'close', u'low', u'high',u'volume’]
        - freq : str                     #默认 D 日线数据
        - precision :str                 #数据精度,默认2
        '''
        self.title=name
        self.data=df.copy()
        self.precision=3
        self.data['f']=self.data.apply(lambda x: self.frb(x.open, x.close), axis = 1)
        
        self.prices_cols = ['open', 'close', 'low', 'high']
        if freq=='D':
            self.dateindex=df.index.strftime("%Y-%m-%d").tolist()
        else:
            self.dateindex=df.index.tolist()
            
    def frb(self,open_value,close_value):
        if (close_value-open_value)>0:
            return 1
        else:
            return -1

        
    def K(self) -> Kline:
        data=self.data[self.prices_cols].values.tolist()
        c = (
            Kline()
            .add_xaxis(self.dateindex)
            .add_yaxis("k线", data)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=self.title, pos_left="0"),
                legend_opts=opts.LegendOpts(
                    is_show=False, pos_bottom=10, pos_left="center"
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=True,
                        xaxis_index=[0, 1],
                        type_="slider",
                        pos_top="85%",
                        range_start=0,
                        range_end=100,
                    ),
                ],
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False),
                                         axistick_opts=opts.AxisTickOpts(is_show=False),),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=2,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    is_show=False,
                    dimension=2,
                    series_index=5,
                    is_piecewise=True,
                    pieces=[
                        {"value": 1, "color": "#00da3c"},
                        {"value": -1, "color": "#ec0000"},
                    ],
                ),
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                brush_opts=opts.BrushOpts(
                    x_axis_index="all",
                    brush_link="all",
                    out_of_brush={"colorAlpha": 0.1},
                    brush_type="lineX",
                ),
            )
        )
        if len(self.klines) != 0:
            kLine = Line().add_xaxis(self.dateindex)
            for i in self.klines:
                kLine.add_yaxis(i, round(self.data[i],self.precision).values.tolist(),
                        is_smooth=True,
                        is_symbol_show=False,
                        is_hover_animation=False,
                        label_opts=opts.LabelOpts(is_show=True),
                        linestyle_opts= opts.LineStyleOpts(type_='solid',width=2),
                )
            kLine.set_global_opts(xaxis_opts=opts.AxisOpts(type_="category",is_show=False))
            c.overlap(kLine)
            
        if 'BUY' in self.data.columns:
            v1 = self.data[self.data['BUY']==True].index.strftime("%Y-%m-%d").tolist()
            v2 = self.data[self.data['BUY']==True]['close']
            es_buy = (
                EffectScatter()
                .add_xaxis(v1)
                .add_yaxis("",v2,symbol=SymbolType.ARROW,is_selected = True)
            )
            c.overlap(es_buy)
        
        if 'SELL' in self.data.columns:
            v1 = self.data[self.data['SELL']==True].index.strftime("%Y-%m-%d").tolist()
            v2 = self.data[self.data['SELL']==True]['low']
            es_sell = (
                EffectScatter()
                .add_xaxis(v1)
                .add_yaxis("",v2)
            )
            c.overlap(es_sell)
        
        return c
    
    
    def V(self)-> Bar:
        db=self.data[['volume','f']].reset_index()
        db['i']=db.index
        ##db['volume']=db.volume.astype('int')
        #print(db[['i','volume','f']].values.tolist())
        v = (
            Bar()
            .add_xaxis(self.dateindex)
            #.add_yaxis("Volume", self.data.volume.values.tolist(),stack="v_stack",category_gap=2,)
            .add_yaxis(
                series_name="成交量", 
                yaxis_data=db[['i','volume','f']].values.tolist(),
                xaxis_index=0,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                        function(params) {
                            var colorList;
                            if (params.data[2] > 0) {
                                colorList = '#ef232a';
                            } else {
                                colorList = '#14b143';
                            }
                            return colorList;
                        }
                        """
                    )
                )
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    is_scale=True,
                    grid_index=1,
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=False),
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=1,
                    is_scale=True,
                    split_number=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axisline_opts=opts.AxisLineOpts(is_show=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                ),
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=False,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                legend_opts=opts.LegendOpts(orient='vertical',pos_left="right",pos_top="70%")
                #legend_opts=opts.LegendOpts(is_show=False),
            )
        )
        if len(self.vlines) != 0:
            vLine = Line().add_xaxis(self.dateindex)
            for i in self.vlines:
                vLine.add_yaxis(series_name=i, 
                        y_axis=round(self.data[i],self.precision).values.tolist(),
                        is_smooth=True,
                        is_symbol_show=False,
                        is_hover_animation=False,
                        label_opts=opts.LabelOpts(is_show=False),
                        linestyle_opts= opts.LineStyleOpts(type_='solid',width=2)
                      )
            vLine.set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
            v.overlap(vLine)
        return v
    
    def MACD(self)-> Bar:
        c = (
            Bar()
            .add_xaxis(self.dateindex)
            .add_yaxis("macd", round(self.data.MACD,self.precision).values.tolist(), stack="v",
                    category_gap=2,
                    itemstyle_opts=opts.ItemStyleOpts(
                            color=JsCode(
                            """
                                function(params) {
                                    var colorList;
                                    if (params.data >= 0) {
                                        colorList = '#ef232a';
                                    } else {
                                        colorList = '#14b143';
                                    }
                                return colorList;
                                }
                            """
                            )
                    ),
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(datazoom_opts=[opts.DataZoomOpts(range_start=0,range_end=100)],
                            legend_opts=opts.LegendOpts(orient='vertical',pos_left="top",pos_top="70%"),
                             xaxis_opts=opts.AxisOpts(
                            type_="category",
                    is_scale=True,
                    grid_index=1,
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=False),)
                            )
        )
        dea = round(self.data.DEA,self.precision).values.tolist()
        dif = round(self.data.DIF,self.precision).values.tolist()
        macd_line = (
            Line()
            .add_xaxis(self.dateindex)
            .add_yaxis("DIF", dif,
                       is_symbol_show=False,
                       label_opts=opts.LabelOpts(is_show=False),
                       linestyle_opts= opts.LineStyleOpts(type_='solid',width=2),
                       
                      )
            .add_yaxis("DEA", dea,
                       is_symbol_show=False,
                       label_opts=opts.LabelOpts(is_show=False)
                      )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(datazoom_opts=[opts.DataZoomOpts()],
                            )
            
        )
        c.overlap(macd_line)
        return c
                                     
    
    def plot(self,area=['V','M'],width=1000,height=680,klines=[],vlines=[])-> Grid:
        '''
        @params:
        - area : list   #显示区域
                       'V'   交易量
                       'M'   k线+MACD
                       FieldName: string   Dataframe中的字段名
                       [Field1,Field2,...] Dataframe中的字段名列表，将显示在一个区域
          width: int   #图表宽度 px
          height:int   #图表高度 px
          klines:str   #K线区域显示的数据，Dataframe中的字段名，如MA...
          vline: str   #Volume区域显示的数据，Dataframe中的字段名，如MA...
        - sample:
           chart=data.plot(area=[['small_pct','medium_pct','big_pct','super_pct'],'V','cci'],vlines=['vMA5','vMA10'],klines=['MA5','MA10'])  
        '''
        self.klines=klines
        self.vlines=vlines 
        grid = (
                Grid(init_opts=opts.InitOpts(
                        width=str(width)+"px",
                        height=str(height)+"px",
                        animation_opts=opts.AnimationOpts(animation=False),
                    )
                )
        )
        c=self.K()
        iTop=10
        iButton=10
        iWindows=len(area)
        iStep=0
        if iWindows==0:
            grid.add(c, grid_opts=opts.GridOpts(pos_top="2%",pos_bottom="10%"))
        elif iWindows>1:
            grid.add(c, grid_opts=opts.GridOpts(pos_top="2%",pos_bottom="50%"))
            iStep=int(30/iWindows)
            iButton=50
        else:
            grid.add(c, grid_opts=opts.GridOpts(pos_top="1%",pos_bottom="30%"))
            iStep=15
            iButton=70
        icount=0
        for w in area:
            #print(iStep)
            if type(w)==list:
                window = Line().add_xaxis(self.dateindex)
                for l in w:
                     window.add_yaxis(series_name=l, 
                        y_axis=round(self.data[l],self.precision).values.tolist(),
                        is_smooth=True,
                        is_symbol_show=False,
                        is_hover_animation=False,
                        label_opts=opts.LabelOpts(is_show=False),
                        linestyle_opts= opts.LineStyleOpts(type_='solid',width=2)
                    )
                window.axislabel_opts=opts.LabelOpts(is_show=False),
                window.set_global_opts(datazoom_opts=[opts.DataZoomOpts()],
                            xaxis_opts=opts.AxisOpts(
                                type_="category",
                                axislabel_opts=opts.LabelOpts(is_show=False),
                            ),
                            legend_opts=opts.LegendOpts(orient='vertical',pos_left="top",pos_top=str(iButton)+"%"),
                )
            
                                           
            elif w=='V':
                window=self.V()
                #grid.add(v,grid_opts=opts.GridOpts(pos_top= str(iButton)+'%',height=str(iStep)+'%'))                
            elif w=='M':
                window=self.MACD()
                #grid.add(macd,grid_opts=opts.GridOpts(pos_top= str(iButton)+'%',height=str(iStep)+'%'))
            else:
                window = Line().add_xaxis(self.dateindex)
                window.add_yaxis(series_name=w, 
                        y_axis=round(self.data[w],self.precision).values.tolist(),
                        is_smooth=True,
                        is_symbol_show=False,
                        is_hover_animation=False,
                        label_opts=opts.LabelOpts(is_show=False),
                        linestyle_opts= opts.LineStyleOpts(type_='solid',width=2)
                      )
                window.axislabel_opts=opts.LabelOpts(is_show=True),
                window.set_global_opts(datazoom_opts=[opts.DataZoomOpts()],
                            xaxis_opts=opts.AxisOpts(
                                type_="category",
                                axislabel_opts=opts.LabelOpts(is_show=False),
                            
                            ),
                            legend_opts=opts.LegendOpts(orient='horizontal',pos_left=str(icount+20)+"%"),
                                       
                )
                if '_'+ w+'_flag' in self.data.columns:
                    #print("find_flag")
                    v1 = self.data[self.data['_'+ w+'_flag']==True].index.strftime("%Y-%m-%d").tolist()
                    v2 = self.data[self.data['_'+ w+'_flag']==True][w]
                    c_flag = (
                        EffectScatter()
                        .add_xaxis(v1)
                        .add_yaxis("",v2)
                    )
                    window.overlap(c_flag)
                #grid.add(vLine,grid_opts=opts.GridOpts(pos_top= str(iButton)+'%',height=str(iStep)+'%')) 
            icount+=1
            #最后一行加上x刻度
            if icount==iWindows:
                window.options['xAxis'][0]['axisLabel'].opts['show']=True
            grid.add(window,grid_opts=opts.GridOpts(pos_top= str(iButton)+'%',height=str(iStep)+'%'))
            iButton=iButton+iStep
        #grid.grid_opts=opts.GridOpts(pos_left="8%", pos_right="8%", height="50%"), 
        grid.options['dataZoom'][0].opts['xAxisIndex']=list(range(0,iWindows+1))
        return grid
    
    def save_png(self,charts,filename):
        make_snapshot(snapshot, charts.render(),filename)
