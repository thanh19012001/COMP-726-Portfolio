// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;

/**
 * @title Storage
 * @dev Modified version of the tutorial Storage contract.
 * Adds a `studentId` variable alongside the original `number` variable,
 * so the contract now stores both a number and a linked Student ID.
 */
contract Storage {

    uint256 number;
    string studentId;

    /**
     * @dev Store a number in the contract
     * @param num value to store
     */
    function store(uint256 num) public {
        number = num;
    }

    /**
     * @dev Return the stored number
     */
    function retrieve() public view returns (uint256){
        return number;
    }

    /**
     * @dev Store a Student ID in the contract
     * @param _studentId the student ID to store
     */
    function setStudentId(string memory _studentId) public {
        studentId = _studentId;
    }

    /**
     * @dev Return the stored Student ID
     */
    function getStudentId() public view returns (string memory) {
        return studentId;
    }
}