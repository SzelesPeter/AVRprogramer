/*
 * PythonAVR.c
 *
 * Created: 10/11/2022 4:21:42 AM
 * Author : Peti Pc
 */ 


//DEFINES------------------------------------------------------------------------------------------
#define F_CPU 16000000 // Clock Speed
#define FOSC 16000000 // Clock Speed
#define BAUD 57600
#define MYUBRR FOSC/16/BAUD-1
#define SPI_DDR DDRB
#define CS      PINB2
#define MOSI    PINB3
#define MISO    PINB4
#define SCK     PINB5

//INCLUDES-----------------------------------------------------------------------------------------
#include <avr/io.h>
#include <avr/delay.h>

//FUNCTION DECLARATIONS-----------------------------------------------------------------------------
void USART_Init( unsigned int );
void USART_Transmit( unsigned char );
unsigned char USART_Receive( void );
void SPI_init();
void SPI_masterTransmitByte( uint8_t );
uint8_t SPI_masterTxRx( uint8_t );
void AVR_Write( char );
void AVR_Read( char );

//MAIN===============================================================================================
int main(void)
{
	SPI_init();
	USART_Init( MYUBRR );
	DDRB |= (1<<1);
	PORTB |= (1<<1);
	char a = 0;

	while (1)
	{	
		a = USART_Receive();
		switch (a)
			{
				case 0x02:
					PORTB &= ~(1<<1);
					USART_Transmit(a);
					break;
				case 0xFF:
					PORTB |= (1<<1);
					USART_Transmit(a);
					break;
				case 0xAC:
					AVR_Write(a);
					break;
				case 0xF0:
					AVR_Write(a);
					break;
				case 0x4D:
					AVR_Write(a);
					break;
				case 0x48:
					AVR_Write(a);
					break;
				case 0x40:
					AVR_Write(a);
					break;
				case 0xC1:
					AVR_Write(a);
					break;
				case 0x4C:
					AVR_Write(a);
					break;
				case 0xC0:
					AVR_Write(a);
					break;
				case 0xC2:
					AVR_Write(a);
					break;
				case 0x28:
					AVR_Read(a);
					break;
				case 0x20:
					AVR_Read(a);
					break;
				case 0xA0:
					AVR_Read(a);
					break;
				case 0x58:
					AVR_Read(a);
					break;
				case 0x30:
					AVR_Read(a);
					break;
				case 0x50:
					AVR_Read(a);
					break;
				case 0x38:
					AVR_Read(a);
					break;
			}
			
	}
}

//FUNCTION DEFINITIONS-----------------------------------------------------------------------------

void AVR_Write( char a )
{
	SPI_masterTransmitByte(a);
	a = USART_Receive();
	SPI_masterTransmitByte(a);
	a = USART_Receive();
	SPI_masterTransmitByte(a);
	a = USART_Receive();
	SPI_masterTransmitByte(a);
	_delay_ms(5);
}

void AVR_Read( char a )
{
	SPI_masterTransmitByte(a);
	a = USART_Receive();
	SPI_masterTransmitByte(a);
	a = USART_Receive();
	SPI_masterTransmitByte(a);
	a = USART_Receive();
	a = SPI_masterTxRx(a);
	USART_Transmit(a);
	
}

void USART_Init( unsigned int ubrr )                     // USART_Init
{                                                       //
	/*Set baud rate */                                 //
	UBRR0H = (unsigned char)(ubrr>>8);                //
	UBRR0L = (unsigned char)ubrr;                    //
	/* Enable receiver and transmitter */           //
    UCSR0B = (1<<RXEN0)|(1<<TXEN0);                //
	/* Set frame format: 8data, 2stop bit */      //
	UCSR0C = (1<<USBS0)|(3<<UCSZ00);             //
}                                               //

void USART_Transmit( unsigned char data )             // USART_Transmit
{                                                    //
	/* Wait for empty transmit buffer */            //
	while ( !( UCSR0A & (1<<UDRE0)) )              //
	;                                             //
	/* Put data into buffer, sends the data */   //
	UDR0 = data;                                //
}                                              //

unsigned char USART_Receive( void )                        // USART_Receive
{                                                         //
	/* Wait for data to be received */                   //
	while ( !(UCSR0A & (1<<RXC0)) )                     //
	;                                                  //
	/* Get and return received data from buffer */    //
	return UDR0;                                     //
}                                                   //


void SPI_init()                                                          // SPI_init
{                                                                       //
	// set CS, MOSI and SCK to output                                  //
	SPI_DDR |= (1 << CS) | (1 << MOSI) | (1 << SCK);                  //
                                                                     //
	// enable SPI, set as master, and clock to fosc/128             //
	SPCR = (1 << SPE) | (1 << MSTR) | (1 << SPR1) | (1 << SPR0);   //
}                                                                 //

void SPI_masterTransmitByte(uint8_t data)     // SPI_masterTransmitByte
{                                            //
	// load data into register              //
	SPDR = data;                           //
                                          //
	// Wait for transmission complete    //
	while(!(SPSR & (1 << SPIF)));       //
}									   //

uint8_t SPI_masterTxRx(uint8_t data)      // SPI_masterTxRx
{                                        //
	// transmit data                    //
	SPDR = data;                       //
                                      //       
	// Wait for reception complete   //
	while(!(SPSR & (1 << SPIF)));   //
                                   //      
	// return Data Register       //
	return SPDR;                 //
}                               //