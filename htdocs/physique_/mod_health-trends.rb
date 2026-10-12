# Health trends module for Physique (BMI・歩数・睡眠のトレンドチャート) 0.3.4 (2026/10/10)
#encoding: utf-8

def physique_module( cgi, db )
  l   = module_lp( db.user.language )
  mod = cgi['mod']

  cfg_ht        = Config.new( db.user, 'health-trends' )
  target_bmi    = cfg_ht.value( 'target_bmi' )
  target_steps  = cfg_ht.value( 'target_steps' )
  target_sleep  = cfg_ht.value( 'target_sleep' )

  target_bmi   = 22.5 if target_bmi.to_s.empty?
  target_steps = 9000 if target_steps.to_s.empty?
  target_sleep = 8 if target_sleep.to_s.empty?

  puts "LOAD bio config<br>" if @debug
  res = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user=?", false, [db.user.name] )&.first
  if res
    unless res['bio'].to_s.empty?
      bio = JSON.parse( res['bio'] )
      height = bio['height'].to_f
    end
  end

  # bio['height'] が無い場合も .to_f で 0.0 になるため、0以下も未設定として扱う
  # (0のままだとBMI計算で0除算になりInfinityがJSONに入ってしまう)
  if height.nil? || height <= 0
    puts l[:error_no_height]
    exit( 0 )
  end

  html_module = ''
  case cgi['step']

  #============================================================
  # FORM: 期間切替UI + 目標値設定（チャート本体はresultsステップで描画）
  #============================================================
  when 'form'
    html_module = <<~HTML
      <div class='row'>
        <div class='col'><h5>#{l[:title]}</h5></div>
      </div>
      <div class='btn-group mb-3' role='group' id='trend-period-group_#{mod}'>
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='24'  onclick='HealthTrendsChartDraw("#{mod}", 24)'>#{l[:period_30]}</a>
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='96'  onclick='HealthTrendsChartDraw("#{mod}", 96)'>#{l[:period_90]}</a>
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='288' onclick='HealthTrendsChartDraw("#{mod}", 288)'>#{l[:period_180]}</a>
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='576' onclick='HealthTrendsChartDraw("#{mod}", 576)'>#{l[:period_365]}</a>
      </div>
      <div class='row mb-3'>
        <div class='col'>
          <div class='input-group input-group-sm'>
            <span class='input-group-text'>#{l[:target_bmi]}</span>
            <input type='number' step='0.1' class='form-control' id='target_bmi_#{mod}' value='#{target_bmi}' onchange='HealthTrendsRedraw("#{mod}")'>
          </div>
        </div>
        <div class='col'>
          <div class='input-group input-group-sm'>
            <span class='input-group-text'>#{l[:target_steps]}</span>
            <input type='number' step='100' class='form-control' id='target_steps_#{mod}' value='#{target_steps}' onchange='HealthTrendsRedraw("#{mod}")'>
          </div>
        </div>
        <div class='col'>
          <div class='input-group input-group-sm'>
            <span class='input-group-text'>#{l[:target_sleep]}</span>
            <input type='number' step='0.1' class='form-control' id='target_sleep_#{mod}' value='#{target_sleep}' onchange='HealthTrendsRedraw("#{mod}")'>
          </div>
        </div>
      </div>
    HTML

  #============================================================
  # RAW: $TB_KOYOMIEX から期間分のトレンドデータをJSONで返す
  #============================================================
  when 'raw'
    days_param  = cgi['days'].to_s
    period_days = %w[24 96 288 576].include?( days_param ) ? days_param.to_i : 24

    to_date   = Date.today
    from_date = to_date - ( period_days - 1 )
    from_str  = from_date.strftime( '%Y-%m-%d' )
    to_str    = to_date.strftime( '%Y-%m-%d' )

    # koyomi設定からどの項目が有効化されているか判定
    kexa = {}
    res = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user=?", false, [db.user.name] )&.first
    if res && !res['koyomi'].to_s.empty?
      begin
        koyomi = JSON.parse( res['koyomi'] )
        kexa   = koyomi['kexa'] || {}
      rescue JSON::ParserError
        kexa = {}
      end
    end

    weight_key = kexa['体重'] == '1' ? '体重' : nil
    steps_key  = kexa['歩数'] == '1' ? '歩数' : nil
    sleep_key  = kexa['睡眠'] == '1' ? '睡眠' : nil

    rows = db.query(
      "SELECT date, cell FROM #{$TB_KOYOMIEX} WHERE user=? AND date >= ? AND date <= ? ORDER BY date ASC",
      false, [db.user.name, from_str, to_str]
    ) || []

    # 注意: row['date']はDB adapterがDateオブジェクトを返すため、
    # 文字列キー(date_str)で引けるよう明示的に .to_s しておく
    cell_by_date = {}
    rows.each do |row|
      key = row['date'].to_s
      begin
        cell_by_date[key] = JSON.parse( row['cell'] )
      rescue JSON::ParserError
        cell_by_date[key] = {}
      end
    end

    # 第1パネルはBMI(体重kg ÷ 身長m²)、歩数・睡眠は生の値をそのまま返す。
    # 目標との差分化は行わない（目標BMIはy軸の中心としてフロント側で使う）。
    trend = { dates: [], bmi: [], steps: [], sleep: [] }
    ( from_date..to_date ).each do |d|
      date_str = d.strftime( '%Y-%m-%d' )
      cell = cell_by_date[date_str] || {}
      # 注意: cell[key] は nil だけでなく空文字列 "" のこともある。
      # Rubyでは "" は truthy なので、単純な真偽判定だと "".to_f が
      # 0 になり「欠測」ではなく「実測値0」として描画されてしまう。
      w = ( weight_key && cell[weight_key].to_s != '' ) ? cell[weight_key] : nil
      s = ( steps_key  && cell[steps_key].to_s  != '' ) ? cell[steps_key]  : nil
      z = ( sleep_key  && cell[sleep_key].to_s  != '' ) ? cell[sleep_key]  : nil
      trend[:dates]  << date_str
#      trend[:steps]  << ( s.nil? ? nil : ( s.to_f - target_steps ))
#      trend[:sleep]  << ( z.nil? ? nil : ( z.to_f - target_sleep ))
      trend[:bmi]    << ( w.nil? ? nil : ( w.to_f / height / height ).round( 2 ))
      trend[:steps]  << ( s.nil? ? nil : s.to_f )
      trend[:sleep]  << ( z.nil? ? nil : z.to_f )
    end

    # 目標値：フォームから送られてきた場合は更新して保存、なければ既存値を維持
    # （チャートへの反映は今は止めているが、保存だけはこれまで通り行う）
    target_bmi    = cgi['target_bmi'].to_s.empty?    ? target_bmi    : cgi['target_bmi'].to_f
    target_steps  = cgi['target_steps'].to_s.empty?  ? target_steps  : cgi['target_steps'].to_i
    target_sleep  = cgi['target_sleep'].to_s.empty?  ? target_sleep  : cgi['target_sleep'].to_f

    cfg_ht.set_value( 'target_bmi',   target_bmi )
    cfg_ht.set_value( 'target_steps', target_steps )
    cfg_ht.set_value( 'target_sleep', target_sleep )
    cfg_ht.update

    trend[:targets] = { bmi: target_bmi, steps: target_steps, sleep: target_sleep }

    puts JSON.generate( trend )
    exit

  #============================================================
  # RESULTS: チャート用div + 描画スクリプト
  #============================================================
  when 'results'
    html_module = "<h6>#{l[:label_bmi_r]}</h6>"
    html_module << "<div id='physique_#{mod}-bmi-chart'></div>"
    html_module << "<h6>#{l[:label_steps_r]}</h6>"
    html_module << "<div id='physique_#{mod}-steps-chart'></div>"
    html_module << "<h6>#{l[:label_sleep_r]}</h6>"
    html_module << "<div id='physique_#{mod}-sleep-chart'></div>"
    html_module << "<div id='physique_#{mod}-no-data' style='display:none;'>#{l[:no_data]}</div>"
    html_module << js_chart( mod, l )
  end

  return html_module
end


def js_chart( mod, l )
  js = <<-"JS"
<script type='text/javascript'>

flashBW();
window.dline = true;
window.dl1 = true;
window.dl2 = true;
displayBW();

if ( typeof window.healthTrendsCharts === 'undefined' ) window.healthTrendsCharts = {};
if ( typeof window.healthTrendsDays === 'undefined' )   window.healthTrendsDays   = {};

var HT_commonMargin = { top: 20, right: 20, bottom: 30, left: 60 };
var HT_chartHeight  = 200;

// ---- 歩数・睡眠パネル専用(積み上げ棒グラフ) -------------------------------
// 1日の棒を「青(目標まで)」「緑(目標を超えた分)」「赤(上限超過分)」の3段で積む。
//   青 = 0 〜 min(目標, 赤の開始値)
//   緑 = 青の上端 〜 赤の開始値   (目標が赤の開始値以上なら緑は出ない = 赤優先)
//   赤 = 赤の開始値 〜 実測値
// 赤の開始値: 歩数は20000歩(固定)、睡眠は 目標+2 時間。
var HT_stackColor = { blue: '#c1e4e9', green: '#3eb370', red: '#e60033' };
var HT_stepsRedStart = 20000;
var HT_sleepRedOver  = 2;

// 3桁区切り(ロケール依存を避けるため en-US 固定)
function healthTrendsFmtComma( v ) { return Math.round( Number( v )).toLocaleString( 'en-US' ); }
function healthTrendsFmtDec1( v )  { return Number( v ).toFixed( 1 ); }

function healthTrendsStackSegments( values, target, redStart ) {
  var a = Math.min( target, redStart );
  var blue = [], green = [], red = [];
  values.forEach( function( v ) {
    if ( v === null || v === undefined ) { blue.push( null ); green.push( null ); red.push( null ); return; }
    blue.push(  Math.min( v, a ));
    green.push( Math.max( 0, Math.min( v, redStart ) - a ));
    red.push(   Math.max( 0, v - redStart ));
  });
  return { blue: blue, green: green, red: red };
}

function healthTrendsBuildStackChart( bindto, label, dates, values, target, redStart, fmt ) {
  var seg = healthTrendsStackSegments( values, target, redStart );
  var ids = [ label + '_1', label + '_2', label + '_3' ];

  // y軸: 最小0、最大は実測値の最大値
  var valid = values.filter( function( v ) { return v !== null && v !== undefined; });
  var maxV  = valid.length ? Math.max.apply( null, valid ) : 0;
  if ( !( maxV > 0 )) maxV = 1;

  var colorMap = {};
  colorMap[ids[0]] = HT_stackColor.blue;
  colorMap[ids[1]] = HT_stackColor.green;
  colorMap[ids[2]] = HT_stackColor.red;

  return c3.generate({
    bindto: bindto,
    padding: HT_commonMargin,
    size: { height: HT_chartHeight },
    data: {
      x: 'x',
      columns: [
        ['x'].concat( dates ),
        [ids[0]].concat( seg.blue ),
        [ids[1]].concat( seg.green ),
        [ids[2]].concat( seg.red )
      ],
      colors: colorMap,
      type: 'bar',
      groups: [ ids ],
      order: null // 系列の並び順どおりに積む(既定の降順だと大きい段が下に来てしまう)
    },
    bar: { width: { ratio: 0.7 }},
    axis: {
      x: { type: 'timeseries', tick: { format: '%m/%d' } },
      y: { min: 0, max: maxV, padding: { top: 0, bottom: 0 }, tick: { format: fmt } }
    },
    legend: { show: false },
    tooltip: {
      show: true,
      // 既定だと3段それぞれの値が並ぶので、その日の実測値(合計)を1行で表示する
      contents: function( d, titleFormat ) {
        var idx   = d[0].index;
        var total = values[idx];
        if ( total === null || total === undefined ) return '';
        var top = seg.red[idx] > 0 ? HT_stackColor.red : ( seg.green[idx] > 0 ? HT_stackColor.green : HT_stackColor.blue );
        return "<table class='c3-tooltip'><tbody>" +
          "<tr><th colspan='2'>" + titleFormat( d[0].x ) + "</th></tr>" +
          "<tr><td class='name'><span style='background-color:" + top + "'></span>" + label + "</td>" +
          "<td class='value'>" + fmt( total ) + "</td></tr></tbody></table>";
      }
    }
  });
}
// ------------------------------------------------------------------------

// ---- BMIパネル専用 ------------------------------------------------------
var HT_bmiColor = { black: '#2b2b2b', high: '#e60033', mid: '#3eb370', low: '#0095d9' };
var HT_bmiBand  = 1; // 目標±1が緑、それより外が赤/青
var HT_bmiOuter = 3; // 目標±3を超えたら黒

function healthTrendsBmiZoneColor( v, target ) {
  if ( v >= target + HT_bmiOuter ) return HT_bmiColor.black;
  if ( v >= target + HT_bmiBand )  return HT_bmiColor.high;
  if ( v <= target - HT_bmiOuter ) return HT_bmiColor.black;
  if ( v <= target - HT_bmiBand )  return HT_bmiColor.low;
  return HT_bmiColor.mid;
}

// y軸: 中心=目標BMI、実測値がはみ出さない最小の対称レンジ。
// 目盛りは目標を中心に等間隔で明示指定する(目標が必ず目盛りに乗るように)。
function healthTrendsBmiAxis( values, target ) {
  var maxDev = 0;
  values.forEach( function( v ) {
    if ( v === null || v === undefined ) return;
    var dev = Math.abs( v - target );
    if ( dev > maxDev ) maxDev = dev;
  });

  var steps = [ 0.5, 1, 2, 5, 10 ];
  var step  = steps[steps.length - 1];
  for ( var i = 0; i < steps.length; i++ ) {
    if ( Math.ceil(( maxDev * 1.05 ) / steps[i] ) <= 3 ) { step = steps[i]; break; }
  }

  // 少なくとも±1.5は見えるようにして、緑の帯の判定が読み取れるようにする
  var n = Math.max( Math.ceil(( maxDev * 1.05 ) / step ), Math.ceil( 1.5 / step ));

  var ticks = [];
  for ( var k = -n; k <= n; k++ ) ticks.push( parseFloat(( target + k * step ).toFixed( 4 )));

  return { min: ticks[0], max: ticks[ticks.length - 1], ticks: ticks };
}

// 折れ線そのものを値の高さに応じて黒/赤/緑/青/黒に塗り分ける。
// 線のバウンディングボックス(データの最小〜最大)に対するグラデーションを、
// 閾値(目標+3, +1, -1, -3)の位置で色がくっきり切り替わるように設定する。
function healthTrendsApplyBmiGradient( bindto, values, target, gradId ) {
  var valid = values.filter( function( v ) { return v !== null && v !== undefined; });
  if ( valid.length === 0 ) return;

  var hi = Math.max.apply( null, valid );
  var lo = Math.min.apply( null, valid );

  var svg  = d3.select( bindto ).select( 'svg' );
  var defs = svg.select( 'defs' );
  if ( defs.empty() ) defs = svg.insert( 'defs', ':first-child' );

  defs.select( '#' + gradId ).remove();

  var stroke;
  if ( hi === lo ) {
    // 値が1種類だけだとバウンディングボックスの高さが0になりグラデーションが効かない
    stroke = healthTrendsBmiZoneColor( hi, target );
  } else {
    var range = hi - lo;
    var off   = function( threshold ) { return Math.max( 0, Math.min( 1, ( hi - threshold ) / range )); }; // 上端(最大値)からの位置
    var oBlackHi = off( target + HT_bmiOuter );
    var oHigh    = off( target + HT_bmiBand );
    var oLow     = off( target - HT_bmiBand );
    var oBlackLo = off( target - HT_bmiOuter );

    var grad = defs.append( 'linearGradient' )
      .attr( 'id', gradId )
      .attr( 'gradientUnits', 'objectBoundingBox' )
      .attr( 'x1', 0 ).attr( 'y1', 0 ).attr( 'x2', 0 ).attr( 'y2', 1 );

    [
      [ 0,        HT_bmiColor.black ],
      [ oBlackHi, HT_bmiColor.black ],
      [ oBlackHi, HT_bmiColor.high  ],
      [ oHigh,    HT_bmiColor.high  ],
      [ oHigh,    HT_bmiColor.mid   ],
      [ oLow,     HT_bmiColor.mid   ],
      [ oLow,     HT_bmiColor.low   ],
      [ oBlackLo, HT_bmiColor.low   ],
      [ oBlackLo, HT_bmiColor.black ],
      [ 1,        HT_bmiColor.black ]
    ].forEach( function( s ) {
      grad.append( 'stop' ).attr( 'offset', s[0] ).attr( 'stop-color', s[1] );
    });

    stroke = 'url(#' + gradId + ')';
  }

  d3.select( bindto ).selectAll( 'path.c3-line' ).style( 'stroke', stroke );
}

function healthTrendsBuildBmiChart( bindto, label, dates, values, target ) {
  var axis   = healthTrendsBmiAxis( values, target );
  var gradId = 'ht-grad-' + bindto.replace( /[^A-Za-z0-9_-]/g, '' );

  return c3.generate({
    bindto: bindto,
    padding: HT_commonMargin,
    size: { height: HT_chartHeight },
    data: {
      x: 'x',
      columns: [
        ['x'].concat( dates ),
        [label].concat( values )
      ],
      colors: { [label]: HT_bmiColor.mid },
      // 点は値ごとに色分け(線はonrenderedでグラデーションを当てる)
      color: function( baseColor, d ) {
        if ( d && typeof d === 'object' && d.value !== null && d.value !== undefined ) {
          return healthTrendsBmiZoneColor( d.value, target );
        }
        return baseColor;
      },
      type: 'line'
    },
    line: { connectNull: true },
    axis: {
      x: { type: 'timeseries', tick: { format: '%m/%d' } },
      y: {
        min: axis.min,
        max: axis.max,
        padding: { top: 0, bottom: 0 },
        tick: {
          values: axis.ticks,
          format: function( v ) { return Number( v ).toFixed( 1 ); }
        }
      }
    },
    point: { r: 3 },
    legend: { show: false },
    tooltip: {
      show: true,
      format: { value: function( v ) { return Number( v ).toFixed( 1 ); } }
    },
    onrendered: function() {
      healthTrendsApplyBmiGradient( bindto, values, target, gradId );
    }
  });
}
// ------------------------------------------------------------------------

async function HealthTrendsChartDraw( mod, days ) {
  days = days || 24;
  window.healthTrendsDays[mod] = days;

  document.querySelectorAll( `#trend-period-group_\${mod} .btn` ).forEach( function( btn ) {
    btn.classList.remove( 'btn-primary' );
    btn.classList.add( 'btn-outline-primary' );
    if ( btn.dataset.days == days ) {
      btn.classList.remove( 'btn-outline-primary' );
      btn.classList.add( 'btn-primary' );
    }
  });

  var targetBMIEl   = document.getElementById( `target_bmi_\${mod}` );
  var targetStepsEl = document.getElementById( `target_steps_\${mod}` );
  var targetSleepEl = document.getElementById( `target_sleep_\${mod}` );
  var targetBMI     = targetBMIEl   ? targetBMIEl.value   : '';
  var targetSteps   = targetStepsEl ? targetStepsEl.value : '';
  var targetSleep   = targetSleepEl ? targetSleepEl.value : '';

  try {
    const rawResponse = await fetch( 'physique.cgi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        mod, step: 'raw', days,
        target_bmi:   targetBMI,
        target_steps: targetSteps,
        target_sleep: targetSleep,
      }),
    });

    if ( !rawResponse.ok ) throw new Error( 'Rawデータ取得に失敗' );

    const raw   = await rawResponse.json();
    const dates = raw.dates;

    // 目標BMI(y軸の中心)。取得できない場合は22.5にフォールバック
    var targetBmiVal = Number(( raw.targets || {} ).bmi );
    if ( !isFinite( targetBmiVal ) || targetBmiVal <= 0 ) targetBmiVal = 22.5;

    // 目標歩数・目標睡眠時間(積み上げ棒グラフの青/緑の境目)。取得できない場合は既定値にフォールバック
    var targetStepsVal = Number(( raw.targets || {} ).steps );
    if ( !isFinite( targetStepsVal ) || targetStepsVal <= 0 ) targetStepsVal = 9000;
    var targetSleepVal = Number(( raw.targets || {} ).sleep );
    if ( !isFinite( targetSleepVal ) || targetSleepVal <= 0 ) targetSleepVal = 8;

    window.healthTrendsCharts[mod] = {
      weight: healthTrendsBuildBmiChart( `#physique_\${mod}-bmi-chart`, '#{l[:label_bmi]}', dates, raw.bmi, targetBmiVal ),
      steps:  healthTrendsBuildStackChart( `#physique_\${mod}-steps-chart`, '#{l[:label_steps]}', dates, raw.steps, targetStepsVal, HT_stepsRedStart, healthTrendsFmtComma ),
      sleep:  healthTrendsBuildStackChart( `#physique_\${mod}-sleep-chart`, '#{l[:label_sleep]}', dates, raw.sleep, targetSleepVal, targetSleepVal + HT_sleepRedOver, healthTrendsFmtDec1 ),
    };

    // NOTE: 3パネル間のカーソル同期(mousemove.sync)は、マウスオーバー時に画面が
    // フリーズする不具合の原因だったため無効化したままです。

  } catch ( error ) {
    console.error( 'HealthTrendsChartDraw エラー:', error );
  }
}

HealthTrendsChartDraw( '#{mod}', 24 );

function HealthTrendsRedraw( mod ) {
  HealthTrendsChartDraw( mod, window.healthTrendsDays[mod] || 24 );
}

</script>
JS

  return js
end


def module_lp( language )
  l = Hash.new
  l['ja'] = {
    mod_name:        "健康トレンド３",
    title:           "健康トレンド３（栄養・運動・休養）",
    period_30:       "1 phase",
    period_90:       "4 phases",
    period_180:      "12 phases",
    period_365:      "24 phases",
    error_no_height: "身長の情報がありません",
    no_data:         "この期間の記録がありません",
    label_bmi:       "BMI",
    label_steps:     "歩数",
    label_sleep:     "睡眠(h)",
    label_bmi_r:     "BMI（kg/m^2）",
    label_steps_r:   "歩数（歩）",
    label_sleep_r:   "睡眠（時間）",
    target_bmi:      "目標BMI",
    target_steps:    "目標歩数",
    target_sleep:    "目標睡眠時間(h)"
  }

  return l[language]
end
