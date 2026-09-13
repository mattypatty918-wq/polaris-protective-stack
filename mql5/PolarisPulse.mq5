//+------------------------------------------------------------------+
//| PolarisPulse.mq5 - Prop detect & heal (public template)           |
//+------------------------------------------------------------------+
#property copyright "Polaris Protective Stack"
#property version   "1.00"

input double RiskPctPerTrade = 0.4;
input double MaxLots = 0.08;
input double DayLossLimitPct = 2.0;
input double HardDDPct = 8.0;
input double SoftDDPct = 5.0;
input int    MaxOpen = 2;
input bool   WriteGateFiles = true;
input int    Magic = 20261102;

double day_start_equity = 0;
double peak_equity = 0;
datetime day_stamp = 0;
int heal_level = 0;

void ResetDayIfNeeded()
{
   MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
   datetime d = StringToTime(StringFormat("%04d.%02d.%02d", dt.year, dt.mon, dt.day));
   if(d != day_stamp)
   {
      day_stamp = d;
      day_start_equity = AccountInfoDouble(ACCOUNT_EQUITY);
      if(peak_equity <= 0) peak_equity = day_start_equity;
      heal_level = 0;
   }
}

double DayLossPct()
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(day_start_equity <= 0) return 0;
   return 100.0 * (eq - day_start_equity) / day_start_equity;
}

double DDPct()
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(eq > peak_equity) peak_equity = eq;
   if(peak_equity <= 0) return 0;
   return 100.0 * (eq - peak_equity) / peak_equity;
}

void WriteGates(int allow_new, double size_mult, string profile)
{
   if(!WriteGateFiles) return;
   int h = FileOpen("phd_entry_gate.txt", FILE_WRITE|FILE_TXT|FILE_COMMON|FILE_ANSI);
   if(h == INVALID_HANDLE) return;
   FileWriteString(h, StringFormat("allow_new=%d\r\n", allow_new));
   FileWriteString(h, StringFormat("size_mult=%.2f\r\n", size_mult));
   FileWriteString(h, StringFormat("max_open=%d\r\n", MaxOpen));
   FileWriteString(h, StringFormat("profile=%s\r\n", profile));
   FileWriteString(h, "by=PolarisPulse\r\n");
   FileClose(h);
}

void DetectAndHeal()
{
   ResetDayIfNeeded();
   double day = DayLossPct();
   double dd = DDPct();
   if(dd <= -HardDDPct || day <= -DayLossLimitPct)
      heal_level = 2;
   else if(dd <= -SoftDDPct || day <= -DayLossLimitPct * 0.7)
      heal_level = MathMax(heal_level, 1);
   else if(day > -0.3 && dd > -SoftDDPct * 0.5)
      heal_level = 0;

   if(heal_level >= 2)
      WriteGates(0, 0.0, "POLARIS_PULSE_HARD_HALT");
   else if(heal_level == 1)
      WriteGates(1, 0.35, "POLARIS_PULSE_SOFT_HEAL");
   else
      WriteGates(1, 1.0, "POLARIS_PULSE_OK");

   Comment("Polaris Pulse | heal=", heal_level,
           " day%=", DoubleToString(day, 2),
           " dd%=", DoubleToString(dd, 2));
}

int OnInit()
{
   day_start_equity = AccountInfoDouble(ACCOUNT_EQUITY);
   peak_equity = day_start_equity;
   DetectAndHeal();
   return INIT_SUCCEEDED;
}

void OnTick()
{
   DetectAndHeal();
}
