# STREAMLIT APP - AI Açıklama Bölümü Güncelleme
# Bu kod parçasını streamlit_app.py'deki "AI Açıklama" bölümüne kopyalayın

with col1:
    st.markdown("### 💬 AI Açıklama")
    
    if analyze_btn or st.session_state.get('last_analysis'):
        with st.spinner(f"🧠 {coin} analiz ediliyor..."):
            
            if AI_AVAILABLE and ai_enabled:
                try:
                    # AI Brain v3 decision
                    decision = ai_brain.make_trading_decision(
                        symbol=coin,
                        interval=timeframe,
                        portfolio_value=10000,
                        risk_per_trade=200
                    )
                    
                    # YENİ: Detaylı açıklama göster
                    detailed_desc = decision.get('detailed_description', '')
                    
                    # Detaylı AI output
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🎯 AI Decision: {decision['decision']} {decision['signal']}</h3>
                        <p><strong>Confidence:</strong> {decision['confidence']*100:.0f}%</p>
                        <p><strong>Score:</strong> {decision['final_score']:.0f}/100</p>
                        <p><strong>Reason:</strong> {decision['reason']}</p>
                        <hr>
                        <h4>📋 Component Analysis:</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # YENİ: Detaylı component breakdown (markdown format)
                    if detailed_desc:
                        st.markdown(detailed_desc)
                    
                    # Risk Metrics
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📊 Risk Metrics:</h4>
                        <p>🎲 Risk of Ruin: {decision['risk_metrics']['risk_of_ruin']:.2f}%</p>
                        <p>📉 Max Drawdown: {decision['risk_metrics']['max_drawdown']:.2f}%</p>
                        <p>📈 Sharpe Ratio: {decision['risk_metrics']['sharpe_ratio']:.2f}</p>
                        <hr>
                        <p>💰 <strong>Position:</strong> ${decision['position_size_usd']:,.2f} ({decision['position_size_pct']:.2f}%)</p>
                        <p>⚠️ <strong>Risk:</strong> ${decision['risk_amount_usd']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Save to session
                    st.session_state['last_decision'] = decision
                    st.session_state['last_analysis'] = True
                
                except Exception as e:
                    st.error(f"❌ AI Brain error: {str(e)}")
                    st.warning("Fallback: Mock data gösteriliyor")
                    
                    # Fallback: Mock data
                    st.markdown("""
                    <div class="metric-card">
                        <h3>⚠️ Zaman dilimleri uyumsuz. Bekle!</h3>
                        <p>📊 Piyasa dalgalı ve tahmin edilemez. Dikkatli ol!</p>
                        <p>💰 Risk/Ödül çok yüksek! 3.8x kazanç potansiyeli.</p>
                        <p>📰 Haberler nötr. Sinyal üzerinde etkisi yok.</p>
                        <p>❌ Güven veya R/R yetersiz. Bekle!</p>
                        <p>📋 Kelly: %2.0 (200 USD)</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # AI disabled - mock data
                st.markdown("""
                <div class="metric-card">
                    <h3>⚠️ AI Brain devre dışı</h3>
                    <p>AI özelliklerini etkinleştirmek için sidebar'dan "AI Brain v3" toggle'ını açın.</p>
                </div>
                """, unsafe_allow_html=True)
