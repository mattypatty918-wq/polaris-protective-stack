// PolarisThunderboltGuard.mq5 - soft limits under 3% day / 6% max DD
#property version "1.00"
input double InpDayLossPct=2.5;
input double InpHardDDPct=5.0;
input double InpMaxLots=0.50;
input int InpMaxOpen=2;
input int InpMaxPerSymbol=1;
input bool InpWriteGates=true;
double day_start_eq=0, peak_eq=0; datetime day_stamp=0; int heal=0;
void ResetDay(){ MqlDateTime dt; TimeToStruct(TimeCurrent(),dt); datetime d=StringToTime(StringFormat("%04d.%02d.%02d",dt.year,dt.mon,dt.day)); if(d!=day_stamp){ day_stamp=d; day_start_eq=AccountInfoDouble(ACCOUNT_EQUITY); if(peak_eq<=0) peak_eq=day_start_eq; heal=0; } }
void WriteGate(int allow,double mult,string profile){ if(!InpWriteGates) return; int f=FileOpen("phd_entry_gate.txt",FILE_WRITE|FILE_TXT|FILE_COMMON|FILE_ANSI); if(f==INVALID_HANDLE) return; FileWriteString(f,StringFormat("allow_new=%d\r\n",allow)); FileWriteString(f,StringFormat("size_mult=%.2f\r\n",mult)); FileWriteString(f,StringFormat("max_open=%d\r\n",InpMaxOpen)); FileWriteString(f,StringFormat("max_lots=%.2f\r\n",InpMaxLots)); FileWriteString(f,StringFormat("profile=%s\r\n",profile)); FileClose(f); }
void OnTick(){ ResetDay(); double eq=AccountInfoDouble(ACCOUNT_EQUITY); if(eq>peak_eq) peak_eq=eq; double dayPct=day_start_eq>0?100.0*(eq-day_start_eq)/day_start_eq:0; double ddPct=peak_eq>0?100.0*(eq-peak_eq)/peak_eq:0; if(ddPct<=-InpHardDDPct||dayPct<=-InpDayLossPct) heal=2; else if(dayPct<=-InpDayLossPct*0.7||ddPct<=-InpHardDDPct*0.6) heal=MathMax(heal,1); else if(dayPct>-0.3) heal=0; if(heal>=2) WriteGate(0,0.0,"THUNDERBOLT_HALT"); else if(heal==1) WriteGate(1,0.35,"THUNDERBOLT_SOFT"); else WriteGate(1,1.0,"THUNDERBOLT_OK"); Comment("TBGuard heal=",heal," day%=",DoubleToString(dayPct,2)," dd%=",DoubleToString(ddPct,2)); }
int OnInit(){ day_start_eq=AccountInfoDouble(ACCOUNT_EQUITY); peak_eq=day_start_eq; return INIT_SUCCEEDED; }
