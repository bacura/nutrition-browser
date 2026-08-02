# Health trends module for Physique (体重・歩数・睡眠のトレンドチャート) 0.3.0 (2026/07/29)
#encoding: utf-8

def physique_module( cgi, db )
  l   = module_lp( db.user.language )
  mod = cgi['mod']

  cfg_ht        = Config.new( db.user, 'health-trends' )
  target_bmi = cfg_ht.value( 'target_bmi' )
  target_steps  = cfg_ht.value( 'target_steps' )
  target_sleep  = cfg_ht.value( 'target_sleep' )

	target_bmi = 22.5 if target_bmi.to_s.empty?
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

	if height.nil?
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
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='30'  onclick='HealthTrendsChartDraw("#{mod}", 30)'>#{l[:period_30]}</a>
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='90'  onclick='HealthTrendsChartDraw("#{mod}", 90)'>#{l[:period_90]}</a>
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='180' onclick='HealthTrendsChartDraw("#{mod}", 180)'>#{l[:period_180]}</a>
        <a href='javascript:void(0)' class='btn btn-sm btn-outline-primary' data-days='365' onclick='HealthTrendsChartDraw("#{mod}", 365)'>#{l[:period_365]}</a>
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
    period_days = %w[30 90 180 365].include?( days_param ) ? days_param.to_i : 90

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
    # (元の単体版では素のオブジェクトのままキーにしていたため、
    #  下のlookupが常にnilを返す不具合があった)
    cell_by_date = {}
    rows.each do |row|
      key = row['date'].to_s
      begin
        cell_by_date[key] = JSON.parse( row['cell'] )
      rescue JSON::ParserError
        cell_by_date[key] = {}
      end
    end

    # 表示は「目標に対する差分比率」(0基準、+が目標超過、-が目標未達)。
    # 例: bmi = 0.1 は「目標BMIより10%高い」、steps = -0.2 は「目標歩数より20%少ない」。
    trend = { dates: [], bmi: [], steps: [], sleep: [] }
    ( from_date..to_date ).each do |d|
      date_str = d.strftime( '%Y-%m-%d' )
      cell = cell_by_date[date_str] || {}
      # 注意: cell[key] は nil だけでなく空文字列 "" のこともある
      # （こよみ拡張の手入力編集で未入力のまま保存されるケース等）。
      # Rubyでは "" は truthy なので、単純な真偽判定だと "".to_f/"".to_i が
      # 0 になり「欠測」ではなく「実測値0」として描画されてしまっていた。
      w = ( weight_key && cell[weight_key].to_s != '' ) ? cell[weight_key] : nil
      s = ( steps_key  && cell[steps_key].to_s  != '' ) ? cell[steps_key]  : nil
      z = ( sleep_key  && cell[sleep_key].to_s  != '' ) ? cell[sleep_key]  : nil
      trend[:dates]  << date_str
      trend[:bmi] << ( w.nil? ? nil : ( ( w.to_f / height / height ) / target_bmi ) - 1 )
      trend[:steps]  << ( s.nil? ? nil : ( s.to_f / target_steps ) - 1 )
      trend[:sleep]  << ( z.nil? ? nil : ( z.to_f / target_sleep ) - 1 )
    end

    # 目標値：フォームから送られてきた場合は更新して保存、なければ既存値を維持
    # ※ 保存する目標値自体は差分化せず、これまで通り「生の目標値」のまま
    #   （表示用ラベル・入力フォームの初期値として使うため）
    target_bmi = cgi['target_bmi'].to_s.empty? ? target_bmi : cgi['target_bmi'].to_f
    target_steps  = cgi['target_steps'].to_s.empty?  ? target_steps  : cgi['target_steps'].to_i
    target_sleep  = cgi['target_sleep'].to_s.empty?  ? target_sleep  : cgi['target_sleep'].to_f

    cfg_ht.set_value( 'target_bmi', target_bmi )
    cfg_ht.set_value( 'target_steps',  target_steps )
    cfg_ht.set_value( 'target_sleep',  target_sleep )
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

if ( typeof window.healthTrendsCharts === 'undefined' ) window.healthTrendsCharts = {};
if ( typeof window.healthTrendsDays === 'undefined' )   window.healthTrendsDays   = {};

var HT_commonMargin = { top: 20, right: 20, bottom: 30, left: 60 };
var HT_chartHeight  = 200; // これまで高さ未指定でC3のデフォルト(目安400px前後)だったものを半分に指定
var HT_yTickFormat  = function( v ) { return v.toFixed( 1 ); };

// 0が常にy軸の中央に来るよう、データの絶対値最大からmin/maxを対称に算出する。
// (C3のデフォルト自動スケールはデータの実際のレンジに合わせるだけなので、
//  プラス側とマイナス側で偏りがあると0が中央に来ない)
function healthTrendsSymmetricAxis( values ) {
  var maxAbs = 0;
  values.forEach( function( v ) {
    if ( v === null || v === undefined ) return;
    var a = Math.abs( v );
    if ( a > maxAbs ) maxAbs = a;
  });
  if ( maxAbs === 0 ) maxAbs = 1; // 全データ欠測・全て0の場合のフォールバック
  maxAbs *= 1.1; // 上下に少し余白を持たせる
  return { min: -maxAbs, max: maxAbs };
}

// 棒グラフ用: プラス/マイナスで色分け（歩数・睡眠パネル）
// 棒は1本ずつ独立した図形のため、data.color コールバックで
// 点ごとに色を切り替えられる。
function healthTrendsBuildChart( bindto, label, dates, values, color, connectNull, type, targetValue, targetLabel, colorSplit ) {
  type = type || 'line';

  var gridConfig = {};
  if ( targetValue !== null && targetValue !== undefined && targetValue !== '' && !isNaN( Number( targetValue ))) {
    gridConfig = {
      y: {
        lines: [
          { value: Number( targetValue ), text: targetLabel, position: 'middle' }
        ]
      }
    };
  }

  var yAxis = healthTrendsSymmetricAxis( values );

  var dataConfig = {
    x: 'x',
    columns: [
      ['x'].concat( dates ),
      [label].concat( values )
    ],
    colors: { [label]: color },
    type: type
  };

  if ( colorSplit ) {
    dataConfig.color = function ( baseColor, d ) {
      if ( typeof d === 'object' && d.value !== null && d.value !== undefined ) {
        return d.value >= 0 ? colorSplit.positive : colorSplit.negative;
      }
      return baseColor;
    };
  }

  return c3.generate({
    bindto: bindto,
    padding: HT_commonMargin,
    size: { height: HT_chartHeight },
    data: dataConfig,
    line: { connectNull: !!connectNull },
    bar:  { width: { ratio: 0.7 }},
    grid: gridConfig,
    axis: {
      x: { type: 'timeseries', tick: { format: '%m/%d' } },
      y: { min: yAxis.min, max: yAxis.max, padding: { top: 0, bottom: 0 }, tick: { format: HT_yTickFormat } }
    },
    point: { r: 3 },
    legend: { show: false },
    tooltip: { show: true }
  });
}

// エリア(面)グラフ用: プラス/マイナスで色分け（BMIパネル）
// 面グラフは1本の連続した塗りのため、棒グラフのような点ごとの
// data.color コールバックでは色分けできない。
// そのため「0以上の値のみの系列」「0未満の値のみの系列」に分割し、
// それぞれ別の面として重ねて描画することで色分けを実現する。
// ※ BMIは「達成/未達成」の概念が人によって逆転しうる(高い/低いどちらが
//   良いかは目標設定次第)ため、歩数・睡眠パネルとは別系統の色を使う。
function healthTrendsBuildSplitAreaChart( bindto, baseLabel, dates, values, targetValue, targetLabel, colorSplit ) {
  var posLabel = baseLabel + '(+)';
  var negLabel = baseLabel + '(-)';

  var posValues = values.map( function( v ) { return ( v === null || v === undefined ) ? null : ( v >= 0 ? v : 0 ); } );
  var negValues = values.map( function( v ) { return ( v === null || v === undefined ) ? null : ( v <  0 ? v : 0 ); } );

  var yAxis = healthTrendsSymmetricAxis( values );

  var gridConfig = {};
  if ( targetValue !== null && targetValue !== undefined && targetValue !== '' && !isNaN( Number( targetValue ))) {
    gridConfig = {
      y: {
        lines: [
          { value: Number( targetValue ), text: targetLabel, position: 'middle' }
        ]
      }
    };
  }

  return c3.generate({
    bindto: bindto,
    padding: HT_commonMargin,
    size: { height: HT_chartHeight },
    data: {
      x: 'x',
      columns: [
        ['x'].concat( dates ),
        [posLabel].concat( posValues ),
        [negLabel].concat( negValues )
      ],
      colors: { [posLabel]: colorSplit.positive, [negLabel]: colorSplit.negative },
      types: { [posLabel]: 'area', [negLabel]: 'area' }
    },
    line: { connectNull: true },
    grid: gridConfig,
    axis: {
      x: { type: 'timeseries', tick: { format: '%m/%d' } },
      y: { min: yAxis.min, max: yAxis.max, padding: { top: 0, bottom: 0 }, tick: { format: HT_yTickFormat } }
    },
    point: { show: false },
    legend: { show: false },
    tooltip: { show: true }
  });
}

async function HealthTrendsChartDraw( mod, days ) {
  days = days || 90;
  window.healthTrendsDays[mod] = days;

  document.querySelectorAll( `#trend-period-group_\${mod} .btn` ).forEach( function( btn ) {
    btn.classList.remove( 'btn-primary' );
    btn.classList.add( 'btn-outline-primary' );
    if ( btn.dataset.days == days ) {
      btn.classList.remove( 'btn-outline-primary' );
      btn.classList.add( 'btn-primary' );
    }
  });

  var targetBMIEl = document.getElementById( `target_bmi_\${mod}` );
  var targetStepsEl  = document.getElementById( `target_steps_\${mod}` );
  var targetSleepEl  = document.getElementById( `target_sleep_\${mod}` );
  var targetBMI   = targetBMIEl ? targetBMIEl.value : '';
  var targetSteps    = targetStepsEl  ? targetStepsEl.value  : '';
  var targetSleep    = targetSleepEl  ? targetSleepEl.value  : '';

  try {
    const rawResponse = await fetch( 'physique.cgi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        mod, step: 'raw', days,
        target_bmi: targetBMI,
        target_steps:  targetSteps,
        target_sleep:  targetSleep,
      }),
    });

    if ( !rawResponse.ok ) throw new Error( 'Rawデータ取得に失敗' );

    const raw     = await rawResponse.json();
    const dates   = raw.dates;
    const targets = raw.targets || {};

    window.healthTrendsCharts[mod] = {
      weight: healthTrendsBuildSplitAreaChart( `#physique_\${mod}-bmi-chart`, '#{l[:label_bmi]}', dates, raw.bmi, 0, '', { positive: '#3498db', negative: '#8e44ad' } ),
      steps:  healthTrendsBuildChart( `#physique_\${mod}-steps-chart`,  '#{l[:label_steps]}',  dates, raw.steps,  '#3498db', false, 'bar',  0, '', { positive: '#2ecc71', negative: '#e67e22' } ),
      sleep:  healthTrendsBuildChart( `#physique_\${mod}-sleep-chart`,  '#{l[:label_sleep]}',  dates, raw.sleep,  '#2ecc71', false, 'bar',  0, '', { positive: '#2ecc71', negative: '#e67e22' } ),
    };

    // NOTE: 3パネル間のカーソル同期(mousemove.sync)は、マウスオーバー時に画面が
    // フリーズする不具合の原因として切り分け中のため、一旦丸ごと無効化しています。
    // 各チャート単体のtooltipはc3標準機能でそのまま動作します。


  } catch ( error ) {
    console.error( 'HealthTrendsChartDraw エラー:', error );
  }
}

HealthTrendsChartDraw( '#{mod}', 90 );

function HealthTrendsRedraw( mod ) {
  HealthTrendsChartDraw( mod, window.healthTrendsDays[mod] || 90 );
}

</script>
JS

  return js
end


def module_lp( language )
  l = Hash.new
  l['ja'] = {
    mod_name:     "健康トレンド３",
    title:        "健康トレンド３（栄養・運動・休養）",
    period_30:    "直近30日",
    period_90:    "直近90日",
    period_180:   "直近180日",
    period_365:   "直近1年",
	error_no_height: "身長の情報がありません",
    no_data:      "この期間の記録がありません",
    label_bmi: "BMI",
    label_steps:  "歩数",
    label_sleep:  "睡眠(h)",
    label_bmi_r: "BMI",
    label_steps_r:  "歩数",
    label_sleep_r:  "睡眠",
    target_bmi: "目標BMI",
    target_steps:  "目標歩数",
    target_sleep:  "目標睡眠時間(h)"	
  }

  return l[language]
end
