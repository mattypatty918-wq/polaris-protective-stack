//+------------------------------------------------------------------+
//| PolarisFade.mq5 - Regime-aware mean reversion (public template)   |
//+------------------------------------------------------------------+
#property copyright "Polaris Protective Stack"
#property version   "1.00"

input double Lots = 0.05;
input double MaxLots = 0.08;
input int    RSIPeriod = 14;
input int    RSIBuyMax = 20;
input int    RSISellMin = 80;
input int    ZLookback = 20;
input double ZEntry = 1.6;
input int    ATRPeriod = 14;
input double SL_ATR_Mult = 1.2;
input double TrailActivateR = 1.15;
input double TrailATRMult = 2.2;
input double RangeMomMax = 0.006;
input double VolMultMax = 1.15;
input int    MaxSpreadPoints = 25;
input int    Magic = 20261101;
input int    MaxOpen = 2;

int hRSI = INVALID_HANDLE, hATR = INVALID_HANDLE, hMA = INVALID_HANDLE;

int OnInit()
{
   hRSI = iRSI(_Symbol, _Period, RSIPeriod, PRICE_CLOSE);
   hATR = iATR(_Symbol, _Period, ATRPeriod);
   hMA  = iMA(_Symbol, _Period, ZLookback, 0, MODE_SMA, PRICE_CLOSE);
   if(hRSI == INVALID_HANDLE || hATR == INVALID_HANDLE || hMA == INVALID_HANDLE)
      return INIT_FAILED;
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   IndicatorRelease(hRSI);
   IndicatorRelease(hATR);
   IndicatorRelease(hMA);
}

bool SpreadOk()
{
   long sp = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   return (sp > 0 && sp <= MaxSpreadPoints);
}

int CountMagic()
{
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!PositionSelectByTicket(PositionGetTicket(i))) continue;
      if(PositionGetInteger(POSITION_MAGIC) == Magic) n++;
   }
   return n;
}

bool HasSymbolMagic()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(!PositionSelectByTicket(PositionGetTicket(i))) continue;
      if(PositionGetInteger(POSITION_MAGIC) == Magic && PositionGetString(POSITION_SYMBOL) == _Symbol)
         return true;
   }
   return false;
}

bool LowVolRange()
{
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(hATR, 0, 0, 30, atr) < 30) return false;
   double sum = 0;
   for(int i = 1; i <= 20; i++) sum += atr[i];
   double avg = sum / 20.0;
   double mom = MathAbs(iClose(_Symbol, _Period, 0) - iClose(_Symbol, _Period, 20)) /
                (iClose(_Symbol, _Period, 20) + 1e-12);
   return (atr[0] <= VolMultMax * avg && mom <= RangeMomMax);
}

double ZScore()
{
   double sum = 0, sum2 = 0;
   for(int i = 0; i < ZLookback; i++)
   {
      double px = iClose(_Symbol, _Period, i);
      sum += px; sum2 += px * px;
   }
   double m = sum / ZLookback;
   double sd = MathSqrt(MathMax(sum2 / ZLookback - m * m, 0));
   if(sd <= 0) return 0;
   return (iClose(_Symbol, _Period, 0) - m) / sd;
}

void OnTick()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
   if(!SpreadOk()) return;
   if(CountMagic() >= MaxOpen) return;
   if(HasSymbolMagic()) return;
   if(!LowVolRange()) return;

   double rsi[], atr[];
   ArraySetAsSeries(rsi, true);
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(hRSI, 0, 0, 2, rsi) < 2) return;
   if(CopyBuffer(hATR, 0, 0, 2, atr) < 2) return;
   double z = ZScore();
   double lots = MathMin(Lots, MaxLots);

   MqlTradeRequest req = {};
   MqlTradeResult res = {};
   req.action = TRADE_ACTION_DEAL;
   req.symbol = _Symbol;
   req.volume = lots;
   req.magic = Magic;
   req.deviation = 20;

   if(rsi[0] < RSIBuyMax && z <= -ZEntry)
   {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      req.type = ORDER_TYPE_BUY;
      req.price = ask;
      req.sl = ask - SL_ATR_Mult * atr[0];
      OrderSend(req, res);
   }
   else if(rsi[0] > RSISellMin && z >= ZEntry)
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      req.type = ORDER_TYPE_SELL;
      req.price = bid;
      req.sl = bid + SL_ATR_Mult * atr[0];
      OrderSend(req, res);
   }
}
