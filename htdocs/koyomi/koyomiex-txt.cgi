#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 koyomi extra TSV 0.0.0 (2026/01/12)


#==============================================================================
#LIBRARY
#==============================================================================
require '../soul'
require '../brain'
require '../body'

#==============================================================================
#STATIC
#==============================================================================
@debug = false
#myself = $KOYOMI_PATH + "/" + File.basename( __FILE__ )


#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		date: "日付"
	}

	return l[language]
end

#==============================================================================
# Main
#==============================================================================
puts "Content-type: text/text\n\n"

user = User.new( @cgi )
db = Db.new( user, @debug, false )
l = language_pack( user.language )


puts "INITIALIZE Date<br>" if @debug
date = Date.today
yyyy = date.year
mm = date.month
dd = date.day
puts "date:#{date.to_time}<br>" if @debug


puts "INITIALIZE calendar<br>" if @debug
calendar = Calendar.new( user, yyyy, mm, dd )
sql_ym = "#{calendar.yyyy}-#{calendar.mm}"


puts "LOAD config<br>" if @debug
start = Time.new.year
kexu = Hash.new
kexa = Hash.new

res = db.query( "SELECT koyomi FROM #{$TB_CFG} WHERE user=?", false, [user.name] )&.first
if res
	unless res['koyomi'].to_s.empty?
		begin
			koyomi = JSON.parse( res['koyomi'] )
    	rescue JSON::ParserError => e
      		puts "J(x_x)P: #{e.message}<br>"
      		koyomi = {}
    	end			
		start = koyomi['start'].to_i unless koyomi['start'].nil?
		kexu = koyomi['kexu'] unless koyomi['kexu'].nil?
		kexa = koyomi['kexa'] unless koyomi['kexa'].nil?
	end
end


puts "tsv Header<br>" if @debug
items = "#{l[:date]}\t"
acts = []
kexu.each do |k, v|
	if kexa[k] == '1'
		items << "#{k} (#{v})\t"
		acts << k
	end
end
items.chop!
items << "\n"
puts items


puts "LOAD date cell<br>" if @debug
cells_date = Hash.new
r = db.query( "SELECT * FROM #{$TB_KOYOMIEX} WHERE user=? AND ( date BETWEEN ? AND ? ) ORDER BY date", false, [user.name, "#{start}-1-1", "#{sql_ym}-#{calendar.ddl}"] )
r.each do |e|
	cells_date[e['date']] = JSON.parse( e['cell'] ) unless e['cell'].to_s.empty?
end


puts "Making TSV<br>" if @debug
day_line = ''
cells_date.each do |date, cell|
	tmp = ''
	acts.each do |item|
		tmp << "#{cell[item].to_s}\t"
	end
	tmp.chop!
	
	unless tmp.gsub( "\t", '' ).empty?
		day_line << "#{date}\t#{tmp}\n"
	end

end
puts day_line


#==============================================================================
# POST PROCESS
#==============================================================================


#==============================================================================
#FRONT SCRIPT
#==============================================================================
