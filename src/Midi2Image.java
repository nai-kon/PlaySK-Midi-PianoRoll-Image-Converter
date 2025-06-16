import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;
import javax.sound.midi.InvalidMidiDataException;
import javax.sound.midi.MetaMessage;
import javax.sound.midi.MidiEvent;
import javax.sound.midi.MidiMessage;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.Sequence;
import javax.sound.midi.ShortMessage;
import javax.sound.midi.Track;

public class Midi2Image {
           
	private int rollDpi = 300;                                                                 
	private int rollTempo = 95;                                                                
	private int rollWidth = (int) (11.25 * this.rollDpi);  // @300dpi                          
	private int rollMargin = 50; // @300dpi                                                    
	private int holeWidth = 18; // @300dpi                                                     
	private int hole0Center = 36; // @300dpi                                                   
	private int hole99Center = 3340; // @300dpi                                                
	private int rollColor = 120; // gray scale              
	private int reducePX = 10;                                                       
	int[][] controlChange2NoteNo = {{64, 18}, {67, 113}};  // Control Change No to Hole No. Sustain/Soft pedals.              
                                                                                               
	private BufferedImage out_img = null;
	private Graphics2D g2d = null;
	       
	Midi2Image(){                    
	}
	
	protected int getHoleX(int note_no) {
		// Return hole x position in pixel by note number 
		return rollMargin + hole0Center + ((note_no - 15) * (hole99Center - hole0Center) / 99) - (holeWidth / 2);
	}

	protected int getTick2Px(long tickLen, int tempo, double bpm, int ppq) {
		// Return hole length in pixel by MIDI tick length
		return (int) ((tickLen * rollDpi * tempo * 1.2) / (bpm * ppq));
	}

	protected void drawHole(int note, int tempo, double bpm, int ppq, long onTick, long offTick) {
		int hole_h = getTick2Px(offTick - onTick, tempo, bpm, ppq) - reducePX;
		hole_h = hole_h < holeWidth ? holeWidth : hole_h; 
		int hole_x = getHoleX(note);
		int hole_y = out_img.getHeight() - getTick2Px(onTick, tempo, bpm, ppq) - hole_h;
		int hole_y_margin = (int) holeWidth / 3;
		int chain_perforation_th_len = 85;
		g2d.setColor(Color.WHITE);
		
		// Chain Perforation
		int y = hole_y;
		for (; y < hole_y + hole_h - chain_perforation_th_len; y += hole_y_margin + holeWidth) {
			g2d.fillOval(hole_x, y, holeWidth, holeWidth);
		}
		// Normal Perforation
		g2d.fillRoundRect(hole_x, y, holeWidth, hole_h - (y - hole_y), holeWidth, holeWidth);
		// somewhow, fillOval() result pops out 1px on left, so fill it.
		g2d.setColor(new Color(rollColor, rollColor, rollColor));
		g2d.drawLine(hole_x, hole_y, hole_x, hole_y + hole_h);
	}
	
	public void convert(String midiPath, String outDir) {
		try {
			Sequence sequence = MidiSystem.getSequence(new File(midiPath));
			int ppq = sequence.getResolution(); // PPQ (ticks per quarter note)
			long totalTickLen = sequence.getTickLength();

			double bpm = 80;
			int tempo = rollTempo;
			
			for (Track track : sequence.getTracks()) {
				long[] noteOnTicks = new long[128];
				for (int i = 0; i < track.size(); i++) {
					MidiEvent evt = track.get(i);
					MidiMessage msg = evt.getMessage();

					if (out_img == null && msg instanceof MetaMessage meta && meta.getType() == 0x51) {
						// Get BPM/Tempo
						byte[] data = meta.getData();
						int tempoMicro = ((data[0] & 0xFF) << 16) | ((data[1] & 0xFF) << 8) | (data[2] & 0xFF);
						bpm = 60_000_000.0 / tempoMicro;
						if (tempo == 0)
							tempo = (int) Math.round(bpm);
						System.out.printf("Tempo event at tick %d: %.2f BPM %d tempo\n", evt.getTick(), bpm, tempo);
						// Create Image Background
						int width = rollWidth + 2 * rollMargin;
						int img_h = getTick2Px(totalTickLen, tempo, bpm, ppq);
						out_img = new BufferedImage(width, img_h, BufferedImage.TYPE_BYTE_GRAY);
						g2d = out_img.createGraphics();
						// Draw Roll Edge
						g2d.setColor(Color.WHITE);
						g2d.fillRect(0, 0, rollMargin, img_h);
						g2d.fillRect(rollWidth + rollMargin, 0, rollMargin, img_h);
						// Draw Roll
						g2d.setColor(new Color(rollColor, rollColor, rollColor));
						g2d.fillRect(rollMargin, 0, rollWidth, img_h);
						g2d.setColor(Color.WHITE);
					}

					if (msg instanceof ShortMessage sm) {
						int cmd = sm.getCommand();
						int note = sm.getData1();
						int velocity = sm.getData2();
						long tick = evt.getTick();

						// Pedal Control Change to Note No
						for (int[] pair : controlChange2NoteNo) {
						    int cc_number = pair[0];
						    int note_numer = pair[1];
							if (cmd == ShortMessage.CONTROL_CHANGE && note == cc_number && velocity > 0) {
								noteOnTicks[note_numer] = tick;
							} else if (cmd == ShortMessage.CONTROL_CHANGE && note == cc_number && velocity == 0) {
								long onTick = noteOnTicks[note_numer];
								drawHole(note_numer, tempo, bpm, ppq, onTick, tick);
							}
						}

						// Note On/Off
						if (cmd == ShortMessage.NOTE_ON && velocity > 0) {
							noteOnTicks[note] = tick;
						} else if (cmd == ShortMessage.NOTE_OFF || cmd == ShortMessage.NOTE_ON && velocity == 0) {
							long onTick = noteOnTicks[note];
							drawHole(note, tempo, bpm, ppq, onTick, tick);
						}
					}
				}
			}	
			// save image
			String save_name = outDir + (new File(midiPath)).getName().replace(".mid", String.format(" tempo%d.png", tempo));
			ImageIO.write(out_img, "png", new File(save_name));
		} catch (InvalidMidiDataException | IOException e) {
			e.printStackTrace();
		}	
	}

	public static void main(String[] args) {

		File dir = new File("C:\\Users\\sasaki\\Downloads\\Ampico_All_erolls\\test\\");
		for (File file : dir.listFiles()) {
		    if (file.isDirectory()) continue;
		    
			var obj = new Midi2Image();
			obj.convert(file.getPath(), "output/classic/");
		}	    		
	}
}