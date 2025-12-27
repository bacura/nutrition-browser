#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 tensei system 0.0.0 (2027/08/01)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )


#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'
require '../body'


#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    tensei:  "転生コード管理",
    code:  "転生コード",
    exp_day:     "有効期限",
    update_day:  "更新日",
    period:  "設定期間",
    status:     "転生クラス",
    new:      "新規作成",
    issue_new:   "新規転生コードを発行",
    issue_ud:   "既存転生コードを更新",
    update:   "更新", 
    delete:   "削除",
    start_day:   "有効日",
    note:   "備考",
    count:   "転生数",
    d1:   "１日",
    m1:   "1ヶ月間",
    y1:   "１年間",
    y10:   "１０年間",
    command:  "操作"
  }

  return l[language]
end

def move_expd( expd, period )
  case period
  when 'd1'
    expd.move_dd( 1 )
  when 'm1'
    expd.move_mm( 1 )
  when 'y1'
    expd.move_yyyy( 1 )
  when 'y10'
    expd.move_yyyy( 10 )
  end

  return expd
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )

if user.status < 8
  puts 'GM error.'
#  exit
end


#### POST
command = @cgi['command']
tensei_code = @cgi['tensei_code'].to_s
status = @cgi['status'].to_i
period = @cgi['period'].to_s
note = @cgi['note'].to_s
yyyymmdd = @cgi['yyyymmdd'].to_s
puts "command:#{command}<br>" if @debug
puts "yyyymmdd:#{yyyymmdd}<br>" if @debug


puts "Date & calendar config<br>" if @debug
yyyy, mm, dd = yyyymmdd.split( '-' )
updd = dd.to_i == 0 ? Calendar.new( user, 0, 0, 0 ) : Calendar.new( user, yyyy.to_i, mm.to_i, dd.to_i ) 


puts "Update flag<br>" if @debug
status_disable = false


case command
when 'delete'
  puts "Deleting tensei<br>" if @debug
  db.query( "DELETE FROM #{$TB_TENSEI} WHERE code=?", true, [tensei_code] )
  tensei_code = ''

when 'issue'
  puts "New entry<br>" if @debug
  expd = Calendar.new( user, yyyy.to_i, mm.to_i, dd.to_i )
  expd = move_expd( expd, period )

  10.times do
    new_tensei_code = SecureRandom.alphanumeric( 4 ) + '-' + SecureRandom.alphanumeric( 4 ) + '-' + SecureRandom.alphanumeric( 4 ) + '-' + SecureRandom.alphanumeric( 4 ) + '-' + SecureRandom.alphanumeric( 4 )
    unless db.query( "SELECT code FROM #{$TB_TENSEI} WHERE code=?", false, [new_tensei_code] )&.first
      db.query( "INSERT INTO #{$TB_TENSEI} SET code=?, period=?, expd=?, updd=?, status=?, note=?", true, [new_tensei_code, period, expd.ymd, updd.ymd, status, note] )
      break
    end
  end

when 'updatef'
  status_disable = true
  res = db.query( "SELECT * FROM #{$TB_TENSEI} WHERE code=?", false, [tensei_code] )&.first
  if res
    status = res['status'].to_i
    period = res['period'].to_s
    note = res['note'].to_s

    yyyy, mm, dd = res['updd'].to_s.split( '-' )
    updd = dd.to_i == 0 ? Calendar.new( user, 0, 0, 0 ) : Calendar.new( user, yyyy.to_i, mm.to_i, dd.to_i ) 
  end

when 'update'
  expd = Calendar.new( user, yyyy.to_i, mm.to_i, dd.to_i )
  expd = move_expd( expd, period )

  db.query( "UPDATE #{$TB_TENSEI} SET period=?, expd=?, updd=?, note=? WHERE code=?", true, [period, expd.ymd, updd.ymd, note, tensei_code] )

  updd = Calendar.new( user, 0, 0, 0 )
  tensei_code = ''
  status = 2
  period = 'd1'
  note = ''
end


puts "tensei list<br>" if @debug
res = db.query( "SELECT * FROM #{$TB_TENSEI} ORDER BY expd;", false )
teisei_html = ''
res.each do |r|
  res2 = db.query( "SELECT COUNT(user) AS tensei_count FROM #{$TB_USER} WHERE tensei=? AND status>0", false, [r['code']] )&.first
  count = res2 ? res2['tensei_count'] : 0

  item = <<~ITEM
  <tr>
    <td>#{r['updd']}</td>
    <td>#{r['expd']}</td>
    <td>#{r['period']}</td>
    <td>#{@account[r['status'].to_i]}</td>
    <td>#{r['code']}</td>
    <td>#{r['note']}</td>
    <td>#{count}</td>
    <td>
      <input type='checkbox' id='update_#{r['code']}'>&nbsp;
      <span class='btn btn-sm btn-warning' onclick="updateTenseiForm( '#{r['code']}' )">#{l[:update]}</span>
      &nbsp;&nbsp;&nbsp;&nbsp;
      <input type='checkbox' id='delete_#{r['code']}'>&nbsp;
      <span class='btn btn-sm btn-danger' onclick="deleteTensei( '#{r['code']}' )">#{l[:delete]}</span>
    </td>
  </tr>
  ITEM
  teisei_html << item
end


puts "HTML parts<br>" if @debug
period_opt = ''
period_h = { 'd1' => l[:d1], 'm1' => l[:m1], 'y1' => l[:y1], 'y10' => l[:y10] }
period_h.each do |k, v|
  period_opt << "<option value='#{k}' #{$SELECT[k == period]}>#{v}</option>"
end

status_opt = ''
@accounts_guild.each do |i|
  status_opt << "<option value='#{i}' #{$SELECT[i == status]}>#{@account[i]}</option>"
end

if tensei_code.empty?
  issue_button = "<button class='btn btn-outline-primary btn-sm' type='button' onclick='issueTenseiCode()'>#{l[:issue_new]}</button>"
else
  issue_button = "<button class='btn btn-warning btn-sm' type='button' onclick=\"updateTensei( '#{tensei_code}' )\">#{l[:issue_ud]}</button>"
end


puts "HTML<br>" if @debug
html = <<~HTML
<div class='container-fluid'>
  <div class='row'>
    <div class='col'><h5>#{l[:tensei]}#{tensei_code.empty? ? '' : ":#{tensei_code}"}</h5></div>
  </div>

  <div class='row'>
    <div class='col-4'>
      <div class='input-group input-group-sm'>
        <label class="input-group-text">#{l[:start_day]}</label>
        <input type='date' class='form-control form-control-sm' id='yyyymmdd' value='#{updd.ymd}'>
      </div>
    </div>

    <div class='col-4'>
      <div class='input-group input-group-sm'>
        <label class="input-group-text">#{l[:period]}</label>
        <select class='form-select form-select-sm' id='period'>#{period_opt}</select>
      </div>
    </div>
    <br>

    <div class='col-4'>
      <div class='input-group input-group-sm'>
        <label class="input-group-text">#{l[:status]}</label>
        <select class='form-select form-select-sm' id='status' #{$DISABLE[status_disable]}>#{status_opt}</select>
      </div>
    </div>
  </div>
  <br>

  <div class='row'>
    <div class='input-group input-group-sm'>
      <label class="input-group-text">#{l[:note]}</label>
      <input type='text' class='form-control form-control-sm' id='note' value='#{note}'>
    </div>
  </div>
  <br>

  <div class='row'>
    #{issue_button}
  </div>
  <br>

  <table class="table table-sm table-hover">
  <thead class='table-light'>
    <tr>
      <td>#{l[:update_day]}</td>
      <td>#{l[:exp_day]}</td>
      <td>#{l[:period]}</td>
      <td>#{l[:status]}</td>
      <td>#{l[:code]}</td>
      <td>#{l[:note]}</td>
      <td>#{l[:count]}</td>
      <td>#{l[:command]}</td>
    </tr>
  </thead>

    #{teisei_html}
  </table>

</div>
HTML

puts html

#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
# FRONT SCRIPT START
#==============================================================================
if command == 'init'
js = <<-"JS"
<script type='text/javascript'>

var issueTenseiCode = () => {
  const yyyymmdd = document.getElementById( "yyyymmdd" ).value;
  const status = document.getElementById( "status" ).value;
  const period = document.getElementById( "period" ).value;
  const note = document.getElementById( "note" ).value;

  postLayer( mp + '#{myself}', 'issue', true, 'L1', { yyyymmdd, status, period, note });
  displayVIDEO( 'Issued' );
};

// Delete tensei code
var deleteTensei = ( tensei_code ) => {
  if( document.querySelector( "#delete_" + tensei_code ).checked ){
    postLayer( mp + '#{myself}', 'delete', true, 'L1', { tensei_code });
    displayVIDEO( 'Deleted' );
  }else{
    displayVIDEO( 'Check!(>_<)' );
  }
};

var updateTenseiForm = ( tensei_code ) => {
  if( document.querySelector( "#update_" + tensei_code ).checked ){
    postLayer( mp + '#{myself}', 'updatef', true, 'L1', { tensei_code });
  }else{
    displayVIDEO( 'Check!(>_<)' );
  }
};


var updateTensei = ( tensei_code ) => {
  const yyyymmdd = document.getElementById( "yyyymmdd" ).value;
  const status = document.getElementById( "status" ).value;
  const period = document.getElementById( "period" ).value;
  const note = document.getElementById( "note" ).value;

  postLayer( mp + '#{myself}', 'update', true, 'L1', { tensei_code, yyyymmdd, status, period, note });
  displayVIDEO( 'Updated' );
};

</script>
JS

  puts js
end

puts '(^q^)' if @debug
