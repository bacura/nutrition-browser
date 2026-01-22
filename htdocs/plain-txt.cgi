#! /usr/bin/ruby
#encoding: utf-8
#fct browser plain text 0.0.3 (2025/12/27)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require './brain'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
  l = Hash.new

  #Japanese
  l['ja'] = {
    round: "四捨五入",
    ceil: "切り上げ",
    floor: "切り捨て",
    weight: "重量",
    gram: "g"
  }

  return l[language]
end

#==============================================================================
# Main
#==============================================================================
puts "Content-type: text/text\n\n"

user = User.new( @cgi )
db = Db.new( user, @debug, false )

puts "Getting GET\n" if @debug
get_data = get_data()
frct_mode = get_data['frct_mode'].to_i
food_weight = BigDecimal( get_data['food_weight'].to_s )
food_no = get_data['food_no']
lg = get_data['lg']
lg = $DEFAULT_LP if lg.to_s.empty?
l = language_pack( lg )


puts "Food weight\n" if @debug
food_weight = 100 if food_weight == nil || food_weight == ''
food_weight = food_weight.to_f


puts "FCT\n" if @debug
res = db.query( "SELECT * FROM #{$TB_FCT} WHERE FN=?", false, [food_no] )&.first
txt = ''
@fct_item.each do |e|
  if e == 'FG' ||  e == 'FN' || e == 'SID' || e == 'Tagnames'
    txt << "#{@fct_name[e]}\t\t#{res[e]}\n"
  else
    t = num_opt( res[e], food_weight, frct_mode, @fct_frct[e] )
    txt << "#{@fct_name[e]}\t#{@fct_unit[e]}\t#{t}\n"
  end
end

fraction = ''
if frct_mode == 1
	fraction = l[:round]
elsif frct_mode == 2
	fraction = l[:ceil]
elsif frct_mode == 3
	fraction = l[:floor]
else
	fraction = l[:round]
end
weight = "#{l[:weight]} #{food_weight} #{l[:gram]} （#{fraction}）\n"


puts weight
puts txt