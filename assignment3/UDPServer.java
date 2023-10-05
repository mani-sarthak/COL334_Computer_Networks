import java.net.InetAddress;
import java.net.DatagramPacket;
import java.security.NoSuchAlgorithmException;
import java.security.MessageDigest;
import java.io.IOException;
import java.io.Reader;
import java.io.BufferedReader;
import java.io.FileReader;
import java.net.DatagramSocket;
import java.util.Hashtable;
import java.util.Random;

// 
// Decompiled by Procyon v0.5.36
// 

public class UDPServer
{
    public static byte[] fileBytes;
    public static int numBytes;
    public static int numLines;
    Random random;
    Hashtable<String, ClientConn> ipAddresses;
    public static DatagramSocket datagramSocket;
    public static boolean variableRate;
    public static boolean tournament;
    public static boolean verbose;
    public static String md5Digest;
    public static int MAXLINES;
    public static int MSS;
    
    public UDPServer() {
        UDPServer.numBytes = 0;
        UDPServer.numLines = 0;
        this.random = new Random();
        this.ipAddresses = new Hashtable<String, ClientConn>();
        UDPServer.tournament = false;
        UDPServer.verbose = false;
    }
    
    public static void main(final String[] array) {
        final UDPServer udpServer = new UDPServer();
        if (array.length < 4) {
            udpServer.log("Usage: java UDPServer [port number] [filename] [maxlines] [variablerate] [tournament] [verbose]");
            return;
        }
        final int int1 = Integer.parseInt(array[0]);
        final String fileName = array[1];
        UDPServer.MAXLINES = Integer.parseInt(array[2]);
        final Random random = new Random(System.currentTimeMillis());
        UDPServer.variableRate = array[3].equals("variablerate");
        UDPServer.tournament = array[4].equals("tournament");
        UDPServer.verbose = array[5].equals("verbose");
        UDPServer.fileBytes = new byte[UDPServer.MAXLINES / 10 * 3072];
        try {
            final BufferedReader bufferedReader = new BufferedReader(new FileReader(fileName));
            String line;
            while (UDPServer.numLines < UDPServer.MAXLINES && (line = bufferedReader.readLine()) != null && line.length() != 0) {
                if (random.nextInt(10) > 3) {
                    initArray(UDPServer.fileBytes, UDPServer.numBytes, line.getBytes());
                    UDPServer.numBytes += line.length();
                    UDPServer.fileBytes[UDPServer.numBytes++] = 10;
                    ++UDPServer.numLines;
                }
            }
            udpServer.log(invokedynamic(makeConcatWithConstants:(I)Ljava/lang/String;, UDPServer.numLines));
            udpServer.log(invokedynamic(makeConcatWithConstants:(I)Ljava/lang/String;, UDPServer.numBytes));
            if (UDPServer.numLines < UDPServer.MAXLINES) {
                for (int i = UDPServer.numLines; i < UDPServer.MAXLINES; ++i) {
                    final String s = invokedynamic(makeConcatWithConstants:(I)Ljava/lang/String;, i);
                    initArray(UDPServer.fileBytes, UDPServer.numBytes, s.getBytes());
                    UDPServer.numBytes += s.length();
                    UDPServer.fileBytes[UDPServer.numBytes++] = 10;
                    ++UDPServer.numLines;
                }
            }
        }
        catch (IOException ex) {
            udpServer.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, ex.getMessage()));
            ex.printStackTrace();
            return;
        }
        try {
            final MessageDigest instance = MessageDigest.getInstance("MD5");
            instance.update(UDPServer.fileBytes, 0, UDPServer.numBytes);
            final byte[] digest = instance.digest();
            final StringBuilder sb = new StringBuilder(digest.length * 2);
            final byte[] array2 = digest;
            for (int length = array2.length, j = 0; j < length; ++j) {
                sb.append(String.format("%02x", array2[j]));
            }
            UDPServer.md5Digest = sb.toString();
            udpServer.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, UDPServer.md5Digest));
        }
        catch (NoSuchAlgorithmException ex2) {
            ex2.printStackTrace();
        }
        try {
            UDPServer.datagramSocket = new DatagramSocket(int1);
            udpServer.log(invokedynamic(makeConcatWithConstants:(I)Ljava/lang/String;, int1));
            while (true) {
                final byte[] buf = new byte[65535];
                try {
                    final DatagramPacket p = new DatagramPacket(buf, buf.length);
                    UDPServer.datagramSocket.receive(p);
                    udpServer.processPacket(p, UDPServer.datagramSocket);
                }
                catch (Exception ex3) {
                    udpServer.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, ex3.getMessage()));
                    ex3.printStackTrace();
                }
            }
        }
        catch (IOException ex4) {
            udpServer.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, ex4.getMessage()));
            ex4.printStackTrace();
        }
    }
    
    public static void initArray(final byte[] array, final int n, final byte[] array2) {
        for (int i = 0; i < array2.length; ++i) {
            array[n + i] = array2[i];
        }
    }
    
    public static void initArray(final byte[] array, final int n, final byte[] array2, final int n2, final int n3) {
        for (int i = 0; i < n3; ++i) {
            array[n + i] = array2[i + n2];
        }
    }
    
    public void processPacket(final DatagramPacket datagramPacket, final DatagramSocket datagramSocket) {
        final InetAddress address = datagramPacket.getAddress();
        final String hostAddress = datagramPacket.getAddress().getHostAddress();
        final int port = datagramPacket.getPort();
        final byte[] data = datagramPacket.getData();
        final long currentTimeMillis = System.currentTimeMillis();
        ClientConn clientConn;
        if ((clientConn = this.ipAddresses.get(hostAddress)) == null) {
            this.ipAddresses.put(hostAddress, clientConn = new ClientConn(hostAddress, currentTimeMillis, this));
        }
        int n = 0;
        int i = 1;
        boolean b = false;
        boolean b2 = false;
        boolean b3 = false;
        boolean b4 = false;
        int int1 = -1;
        int int2 = -1;
        String substring = "";
        String substring2 = "";
        while (i != 0) {
            final StringBuilder sb = new StringBuilder();
            while (data[n] >= 32 && data[n] < 127 && n < data.length) {
                sb.append((char)data[n++]);
            }
            if (data[n] == 10) {
                final String string = sb.toString();
                if (UDPServer.verbose) {
                    this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;, hostAddress, string));
                }
                if (string.startsWith("Offset")) {
                    int1 = Integer.parseInt(string.substring("Offset: ".length()));
                    b2 = true;
                }
                else if (string.startsWith("NumBytes")) {
                    int2 = Integer.parseInt(string.substring("NumBytes: ".length()));
                    b2 = true;
                }
                else if (string.startsWith("SendSize")) {
                    b = true;
                }
                else if (string.startsWith("Submit")) {
                    substring = string.substring("Submit: ".length());
                    b3 = true;
                }
                else if (string.startsWith("MD5")) {
                    substring2 = string.substring("MD5: ".length());
                    b3 = true;
                }
                else if (string.startsWith("Reset")) {
                    b4 = true;
                }
                else if (string.length() == 0) {
                    i = 0;
                }
                ++n;
            }
            else {
                final String s = "ERROR: Invalid characters in header\n\n";
                this.sendPacket(datagramSocket, address, port, s.getBytes(), 0, s.length());
                if (!UDPServer.verbose) {
                    continue;
                }
                this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, hostAddress));
            }
        }
        if (b) {
            final String s2 = invokedynamic(makeConcatWithConstants:(I)Ljava/lang/String;, UDPServer.numBytes);
            this.sendPacket(datagramSocket, address, port, s2.getBytes(), 0, s2.length());
            if (UDPServer.verbose) {
                this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;I)Ljava/lang/String;, hostAddress, UDPServer.numBytes));
            }
        }
        if (b2) {
            if (int1 < 0 || int2 < 0 || int2 > UDPServer.MSS || int1 >= UDPServer.numBytes) {
                final String s3 = "ERROR: Required header info not received\n\n";
                this.sendPacket(datagramSocket, address, port, s3.getBytes(), 0, s3.length());
                if (UDPServer.verbose) {
                    this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, hostAddress));
                }
            }
            else if (clientConn.sendOrSkipData(currentTimeMillis)) {
                final byte[] array = new byte[65535];
                final int min = Math.min(UDPServer.numBytes - int1 + 1, int2);
                final String s4 = new String(invokedynamic(makeConcatWithConstants:(II)Ljava/lang/String;, int1, min));
                String s5;
                if (clientConn.isSquished()) {
                    s5 = invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, s4);
                }
                else {
                    s5 = invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, s4);
                }
                initArray(array, 0, s5.getBytes());
                initArray(array, s5.length(), UDPServer.fileBytes, int1, min);
                this.sendPacket(datagramSocket, address, port, array, 0, s5.length() + min);
                if (UDPServer.verbose) {
                    this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;IIZ)Ljava/lang/String;, hostAddress, int1, min, clientConn.isSquished()));
                }
            }
            else if (UDPServer.verbose) {
                this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;I)Ljava/lang/String;, hostAddress, int1));
            }
        }
        if (b3) {
            if (substring.equals("") || substring2.equals("")) {
                final String s6 = "ERROR: Team name or MD5 not received\n\n";
                this.sendPacket(datagramSocket, address, port, s6.getBytes(), 0, s6.length());
                if (UDPServer.verbose) {
                    this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, hostAddress));
                }
            }
            else if (substring2.equals(UDPServer.md5Digest)) {
                final String s7 = invokedynamic(makeConcatWithConstants:(JI)Ljava/lang/String;, currentTimeMillis - clientConn.getSessionStartTime(), clientConn.getCumulPenalty());
                this.sendPacket(datagramSocket, address, port, s7.getBytes(), 0, s7.length());
                this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;JII)Ljava/lang/String;, hostAddress, currentTimeMillis - clientConn.getSessionStartTime(), clientConn.getCumulPenalty(), clientConn.getRunningPenalty()));
            }
            else {
                final String s8 = invokedynamic(makeConcatWithConstants:(JI)Ljava/lang/String;, currentTimeMillis - clientConn.getSessionStartTime(), clientConn.getCumulPenalty());
                this.sendPacket(datagramSocket, address, port, s8.getBytes(), 0, s8.length());
                this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;JII)Ljava/lang/String;, hostAddress, currentTimeMillis - clientConn.getSessionStartTime(), clientConn.getCumulPenalty(), clientConn.getRunningPenalty()));
            }
        }
        if (b4 && !UDPServer.tournament) {
            clientConn.reset(currentTimeMillis);
        }
    }
    
    public synchronized void sendPacket(final DatagramSocket datagramSocket, final InetAddress address, final int port, final byte[] buf, final int offset, final int length) {
        try {
            datagramSocket.send(new DatagramPacket(buf, offset, length, address, port));
        }
        catch (Exception ex) {
            this.log(invokedynamic(makeConcatWithConstants:(Ljava/lang/String;)Ljava/lang/String;, ex.getMessage()));
            ex.printStackTrace();
        }
    }
    
    public boolean loss(final int n) {
        return this.random.nextInt(100) <= n;
    }
    
    public synchronized void log(final String x) {
        System.out.println(x);
    }
    
    public synchronized void log(final byte[] array, final int n) {
        for (int i = 0; i < n; ++i) {
            System.out.print((char)array[i]);
        }
    }
    
    static {
        UDPServer.md5Digest = "";
        UDPServer.MAXLINES = 200;
        UDPServer.MSS = 1448;
    }
}
