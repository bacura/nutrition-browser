# Detective module Simulated Annealing 0.1.0 (2026/03/30)
#encoding: utf-8
module DetectiveMod_02_Simulated_Annealing
  def self.lp( language )
    l = { 'ja' => { mod_name: "焼きなまし法（最大10食品）" }}
    return l[language]
  end

  def self.calc_score( foods, weights, std_target, sw )
    en = pr = fa = ca = sa = 0
    weights.each_with_index do |w, i|
      en += foods[i]['energy']  * w
      pr += foods[i]['protein'] * w
      fa += foods[i]['fat']     * w
      ca += foods[i]['carb']    * w
      sa += foods[i]['salt']    * w
    end
    ( ( std_target[:energy]  - en ) ** 2 ) * sw[:e] +
    ( ( std_target[:protein] - pr ) ** 2 ) * sw[:p] +
    ( ( std_target[:fat]     - fa ) ** 2 ) * sw[:f] +
    ( ( std_target[:carb]    - ca ) ** 2 ) * sw[:c] +
    ( ( std_target[:salt]    - sa ) ** 2 ) * sw[:s]
  end

  def self.detective_module( foods, std_target, cfg )
    foods = foods.first( 10 )
    n = foods.size

    total = std_target[:energy] + std_target[:protein] + std_target[:fat] + std_target[:carb] + std_target[:salt]
    sw = {
      e: ( total / ( std_target[:energy]  == 0 ? 0.1 : std_target[:energy]  ) ) ** 2,
      p: ( total / ( std_target[:protein] == 0 ? 0.1 : std_target[:protein] ) ) ** 2,
      f: ( total / ( std_target[:fat]     == 0 ? 0.1 : std_target[:fat]     ) ) ** 2,
      c: ( total / ( std_target[:carb]    == 0 ? 0.1 : std_target[:carb]    ) ) ** 2,
      s: ( total / ( std_target[:salt]    == 0 ? 0.1 : std_target[:salt]    ) ) ** 2
    }

    # 初期重量をランダムに設定
    weights = Array.new( n ) { rand * 100 }
    total_w = weights.sum
    weights.map! { |w| w / total_w * 100 }

    score = calc_score( foods, weights, std_target, sw )
    best_weights = weights.dup
    best_score = score

    # 焼きなまし法パラメータ
    temp = 10000.0
    temp_min = 0.01
    cooling = 0.9999  # 約180000回
    step = 5.0        # 変動幅を大きく

    while temp > temp_min
      # ランダムに2つの食品を選んで重量を移動
      i = rand( n )
      j = rand( n )
      next if i == j

      delta = rand * step * 2 - step  # -step ~ +step
      new_weights = weights.dup
      new_weights[i] += delta
      new_weights[j] -= delta

      # 重量が負にならないようにガード
      next if new_weights[i] < 0.1
      next if new_weights[j] < 0.1

      new_score = calc_score( foods, new_weights, std_target, sw )
      delta_score = new_score - score

      if delta_score < 0 || rand < Math.exp( -delta_score / temp )
        weights = new_weights
        score = new_score

        if score < best_score
          best_score = score
          best_weights = weights.dup
        end
      end

      temp *= cooling
    end

    best_weights.map { |w| w.round( 1 ) }
  end
end