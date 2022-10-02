    
    
DROP TABLE IF EXISTS things;
DROP TABLE IF EXISTS boards;

CREATE TABLE boards(
   id INT GENERATED ALWAYS AS IDENTITY,
   name VARCHAR(255) NOT NULL,
   PRIMARY KEY(id)
);

CREATE TABLE things(
   id INT GENERATED ALWAYS AS IDENTITY,
   board_id INT,
   mac_address VARCHAR(17) NOT NULL,
   name VARCHAR(255),
   PRIMARY KEY(thing_id),
   CONSTRAINT fk_board
      FOREIGN KEY(board_id) 
	  REFERENCES boards(id)
);