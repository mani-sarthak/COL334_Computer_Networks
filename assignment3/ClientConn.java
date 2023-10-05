// 
// Decompiled by Procyon v0.5.36
// 

class ClientConn
{
    UDPServer server;
    String ipAddr;
    long sessionStartTime;
    long lastDataSentTime;
    static int MAXRATE;
    static int MINRATE;
    int RATE;
    int BUCKET;
    int LOSSRATE;
    int tokens;
    int cumulPenalty;
    int penalty;
    int rateReset;
    int squishTime;
    int numSquishes;
    int currSlot;
    
    public ClientConn(final String ipAddr, final long sessionStartTime, final UDPServer server) {
        this.sessionStartTime = -1L;
        this.lastDataSentTime = -1L;
        this.RATE = ClientConn.MAXRATE;
        this.BUCKET = 10;
        this.LOSSRATE = 10;
        this.tokens = 0;
        this.cumulPenalty = 0;
        this.penalty = 0;
        this.rateReset = 0;
        this.squishTime = 0;
        this.numSquishes = 0;
        this.currSlot = 0;
        this.ipAddr = ipAddr;
        this.sessionStartTime = sessionStartTime;
        this.server = server;
    }
    
    public boolean sendOrSkipData(final long lastDataSentTime) {
        if (this.lastDataSentTime == -1L) {
            this.tokens = (int)Math.min((lastDataSentTime - this.sessionStartTime) / 1000.0 * this.RATE, this.BUCKET);
        }
        else {
            this.tokens += (int)Math.min((lastDataSentTime - this.lastDataSentTime) / 1000.0 * this.RATE, this.BUCKET - this.tokens);
        }
        final UDPServer server = this.server;
        if (UDPServer.verbose) {
            this.server.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;III)Ljava/lang/String;, this.ipAddr, this.tokens, this.cumulPenalty, this.penalty));
        }
        if (this.tokens <= 0) {
            ++this.cumulPenalty;
            ++this.penalty;
            if (this.squishTime == 0 && this.penalty > 100) {
                this.squishTime = 100;
                this.penalty = 0;
                ++this.numSquishes;
                this.RATE = ClientConn.MINRATE;
            }
            final UDPServer server2 = this.server;
            if (UDPServer.verbose) {
                this.server.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;II)Ljava/lang/String;, this.ipAddr, this.penalty, this.squishTime));
            }
            return false;
        }
        if (this.squishTime > 0) {
            --this.squishTime;
            if (this.squishTime == 0) {
                this.RATE = ClientConn.MAXRATE;
            }
        }
        this.variableRateChange(lastDataSentTime);
        if (!this.server.loss(this.LOSSRATE)) {
            this.lastDataSentTime = lastDataSentTime;
            --this.tokens;
            return true;
        }
        return false;
    }
    
    public void variableRateChange(final long n) {
        if (this.squishTime == 0) {
            final UDPServer server = this.server;
            if (UDPServer.variableRate && (n - this.sessionStartTime) / 2000L % 2L != this.currSlot) {
                if (this.currSlot > 0) {
                    this.RATE = ClientConn.MAXRATE * 4;
                    final UDPServer server2 = this.server;
                    if (UDPServer.verbose) {
                        this.server.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;J)Ljava/lang/String;, this.ipAddr, n - this.sessionStartTime));
                    }
                }
                else {
                    this.RATE = ClientConn.MAXRATE / 2;
                    final UDPServer server3 = this.server;
                    if (UDPServer.verbose) {
                        this.server.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;J)Ljava/lang/String;, this.ipAddr, n - this.sessionStartTime));
                    }
                }
                this.currSlot = 1 - this.currSlot;
            }
        }
    }
    
    public long getSessionStartTime() {
        return this.sessionStartTime;
    }
    
    public int getCumulPenalty() {
        return this.cumulPenalty;
    }
    
    public int getRunningPenalty() {
        return this.penalty;
    }
    
    public boolean isSquished() {
        return this.squishTime > 0;
    }
    
    public void reset(final long sessionStartTime) {
        this.sessionStartTime = sessionStartTime;
        this.lastDataSentTime = -1L;
        this.RATE = ClientConn.MAXRATE;
        this.tokens = 0;
        this.cumulPenalty = 0;
        this.penalty = 0;
        this.rateReset = 0;
        this.squishTime = 0;
        this.currSlot = 0;
        this.numSquishes = 0;
    }
    
    static {
        ClientConn.MAXRATE = 250;
        ClientConn.MINRATE = ClientConn.MAXRATE / 4;
    }
}
